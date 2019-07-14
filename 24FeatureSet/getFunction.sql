set search_path to mimic3;
--- get the feature out base on the required time interval
--DROP FUNCTION get_pvt_sofa_f20(icustay_id bigint, time_window integer);
--offline temporary

--select * from get_pvt_sofa_f20(261176,1);
--select * from get_locf_pvt_sofa_f20(261176,1);
--select * from get_score_locf_pvt_sofa_f20(261176,1);
--select * from get_mask_sofa_f20(261176,1);
select * from get_feature_f20(261176,1);
