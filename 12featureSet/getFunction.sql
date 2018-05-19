set search_path to mimic3;
--- get the feature out base on the required time interval
create or replace function get_pvt_sofa(icustay_id bigint, time_window integer)
	returns table (
	TW_hour_idx double precision, 
    ABP_mean double precision,
    Bilirubin double precision, 
    CREATININE double precision,
    Dobutamine double precision,
    Dopamine double precision,
    Epinephrine double precision,   
    FiO2 double precision,
    GCS double precision,
    Norepinephrine double precision,
    PaO2 double precision,
    Platelets double precision,
    URINE double precision	
	) 
as $$
declare
	tw_string text;
	qtext text;
	
begin
	tw_string = format('tw_%shr',time_window);
	qtext =format('select %s, lower(itemcat),
		case			
			when lower(itemcat)=''urine'' then 
				(select (urine_output_per_24hrs * %s / 24) 
				from mt_adults_daily_urine_outputs mt_urine 
				where mt_urine.icustay_id= %s 
				and tw_24hr = floor(%s * %s / 24) +1)
			else avg(valuenum)	
		end valuenum
	from mt_adults_sofa_vars_tw where icustay_id=%s and valuenum>0
	group by %s, itemcat
	order by %s',tw_string,time_window,icustay_id,tw_string, time_window, icustay_id, tw_string, tw_string);
	return query select *
	from crosstab(qtext, 'select lower(item_cat) from d_sofa_vars order by item_cat')
	as pvt(
	TW_hour_idx double precision,     ABP_mean double precision,
    Bilirubin double precision,     CREATININE double precision,
    Dobutamine double precision,    Dopamine double precision,
    Epinephrine double precision,    FiO2 double precision,
    GCS double precision,    Norepinephrine double precision,
    PaO2 double precision,    Platelets double precision,
    URINE double precision	
	);
end;
$$ language plpgsql;	

----get the feature out base on the required time interval and fill missing value
create or replace function get_locf_pvt_sofa(icustay_id bigint, time_window integer)
	returns table (
		tw_hour_idx double precision, 
		abp_mean double precision,
		bilirubin double precision,	
		creatinine double precision,
		dobutamine double precision, -- not to impute
		dopamine double precision, -- not to impute
		epinephrine double precision,	-- not to impute
		fio2 double precision,
		gcs double precision,
		norepinephrine double precision,  -- not to impute
		pao2 double precision,
		platelets double precision,
		urine double precision
	) 
as $$
begin
	return query
	select pvt_sofa.tw_hour_idx,
	    case -- abp_mean
	        when locf(pvt_sofa.abp_mean) OVER( ORDER BY pvt_sofa.tw_hour_idx ) is null 
	            then (select distinct median_value from d_sofa_vars where lower(item_cat)='abp_mean')
	        else locf(pvt_sofa.abp_mean) OVER( ORDER BY pvt_sofa.tw_hour_idx )
	    end abp_mean,

	    case -- bilirubin
	        when locf(pvt_sofa.bilirubin) OVER( ORDER BY pvt_sofa.tw_hour_idx ) is null 
	            then (select distinct median_value from d_sofa_vars where lower(item_cat)='bilirubin')
	        else locf(pvt_sofa.bilirubin) OVER( ORDER BY pvt_sofa.tw_hour_idx )
	    end bilirubin,

	    case -- creatinine
	    	when locf(pvt_sofa.creatinine) OVER( ORDER BY pvt_sofa.tw_hour_idx ) is null 
	    		then (select distinct median_value from d_sofa_vars where lower(item_cat)='creatinine')
	        else locf(pvt_sofa.creatinine) OVER( ORDER BY pvt_sofa.tw_hour_idx )
	    end creatinine,
	    pvt_sofa.dobutamine,
	    pvt_sofa.dopamine,
	    pvt_sofa.epinephrine,
	    case -- fio2
	        when locf(pvt_sofa.fio2) OVER( ORDER BY pvt_sofa.tw_hour_idx ) is null 
	            then (select distinct median_value from d_sofa_vars where lower(item_cat)='fio2')
	        else locf(pvt_sofa.fio2) OVER( ORDER BY pvt_sofa.tw_hour_idx )
	    end fio2,

	    case -- gcs
	    	when locf(pvt_sofa.gcs) OVER( ORDER BY pvt_sofa.tw_hour_idx ) is null 
	    		then (select distinct median_value from d_sofa_vars where lower(item_cat)='gcs')
	        else locf(pvt_sofa.gcs) OVER( ORDER BY pvt_sofa.tw_hour_idx )
	    end gcs,
	    pvt_sofa.norepinephrine,
	    case -- pao2
	        when locf(pvt_sofa.pao2) OVER( ORDER BY pvt_sofa.tw_hour_idx ) is null 
	            then (select distinct median_value from d_sofa_vars where lower(item_cat)='pao2')
	        else locf(pvt_sofa.pao2) OVER( ORDER BY pvt_sofa.tw_hour_idx )
	    end pao2,    

	    case -- platelets
	    	when locf(pvt_sofa.platelets) OVER( ORDER BY pvt_sofa.tw_hour_idx ) is null 
	    		then (select distinct median_value from d_sofa_vars where lower(item_cat)='platelets')
	        else locf(pvt_sofa.platelets) OVER( ORDER BY pvt_sofa.tw_hour_idx )
	    end platelets,

	    case -- urine
--	    (select (urine_output_per_24hrs * time_window / 24) from mt_adults_daily_urine_outputs mt_urine
--	    	where mt_urine.icustay_id= icustay_id
--	    	and tw_24hr = floor(pvt_sofa.tw_hour_idx * time_window / 24) +1) urine
	    	when locf(pvt_sofa.urine) OVER( ORDER BY pvt_sofa.tw_hour_idx ) is null 
	    		then 0 --(select distinct median_value from d_sofa_vars where lower(item_cat)='urine')
	        else locf(pvt_sofa.urine) OVER( ORDER BY pvt_sofa.tw_hour_idx )
	    end urine
	from (select * from get_pvt_sofa($1,$2)) pvt_sofa;

end;
$$ language plpgsql;


----get score
create or replace function get_score_locf_pvt_sofa(icustay_id bigint, time_window integer)
	returns table (
		tw_hour_idx double precision,
		total_sofa_score integer
		)
as $$
begin
	return query 
		select 	scores_sheet.tw_hour_idx, cardiovascular_points + respiration_points + creatinine_points +
			gcs_points + bilirubin_points + platelets_points + urine_points
			as total_sofa_score from
		(
			select locf_pvt_sofa.tw_hour_idx,
				case -- Cardiovascular Points
					when (abp_mean>=70) and (dopamine is null) and (dobutamine is null) and (epinephrine is null) and (norepinephrine is null)  then 0
					when (abp_mean<70) and (dopamine is null) and (dobutamine is null) and (epinephrine is null) and (norepinephrine is null) then 1 
					when (dopamine<=5) or (dobutamine is not null) then 2
					when ((dopamine>5) and (dopamine<=15)) or ((epinephrine >0) and (epinephrine <=0.1)) or ((norepinephrine >0) and (norepinephrine<=0.1)) then 3
					when (dopamine>15) or (epinephrine>0.1) or (norepinephrine>0.1) then 4
					else 0
				end cardiovascular_points, 

				case -- Respiration Points
					when pao2/(fio2/100) <100 then 4
					when pao2/(fio2/100) <200 then 3
					when pao2/(fio2/100) <300 then 2
					when pao2/(fio2/100) <400 then 1
					when pao2/(fio2/100) >=400 then 0
				end respiration_points, 	

				case -- CREATININE Points
					when creatinine<1.2 then 0
					when creatinine<=1.9 then 1
					when creatinine<=3.4 then 2
					when creatinine<=4.9 then 3
					when creatinine>4.9 then 4 --(equation >=5)
				end creatinine_points,

				case -- GCS Points
					when gcs<6 then 4
					when gcs<=9 then 3
					when gcs<=12 then 2
					when gcs<=14 then 1
					when gcs=15 then 0
				end gcs_points,

				case -- Bilirubin Points
					when bilirubin<=1.2 then 0
					when bilirubin<=1.9 then 1
					when bilirubin<=5.9 then 2
					when bilirubin<=11.9 then 3
					when bilirubin>11.9 then 4 --(equation >=12)
				end bilirubin_points,

				case -- Platelets Points
					when platelets<20 then 4
					when platelets<50 then 3
					when platelets<100 then 2
					when platelets<150 then 1
					when platelets>=150 then 0 
				end platelets_points,

				case -- Urine Points
					when urine<(($2*0.2)/24) then 4
					when urine<(($2*0.5)/24) then 3 
					else 0
				end urine_points	
			from (select * from get_locf_pvt_sofa($1,$2)) locf_pvt_sofa
		) as scores_sheet;

end;
$$ language plpgsql;


select * from get_pvt_sofa(261176,1)
select * from get_locf_pvt_sofa(261176,1)
select * from get_score_locf_pvt_sofa(261176,1)
