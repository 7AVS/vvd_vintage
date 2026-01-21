# ODS_HIST Table Metadata

**Full Table Path:** `prod_x610_crm.ods_hist`

## Schema

| Column Name | Data Type |
|-------------|-----------|
| offr_id | varchar(20) |
| clnt_id | int |
| chnl_cd | int |
| acct_no | string |
| tactic_id | varchar(10) |
| camp_reg_id | string |
| lang_cd | varchar(10) |
| tr_no | int |
| acct_sufx_no | int |
| prod_id | string |
| prod_mn | string |
| est_mail_dt | varchar(10) |
| campgn_cd | int |
| delvry_mthd_cd | varchar(10) |
| foll_up_mthd_cd | varchar(10) |
| offr_strt_dt | varchar(10) |
| offr_end_dt | varchar(10) |
| updt_untl_dt | varchar(10) |
| offr_displ_cd | varchar(10) |
| offr_sts_cd | int |
| offr_reas_cd | int |
| updt_tmstmp | varchar(20) |
| updt_emp_no | int |
| updt_chnl_cd | int |
| msg_creat_tmstmp | varchar(20) |
| prirty_scor | string |
| cr_crd_no | varchar(20) |
| oper_id | varchar(10) |
| instrmt_no | varchar(10) |
| csdb_offr_strt_dt | varchar(10) |
| csdb_offr_end_dt | varchar(10) |
| csdb_tactic_id | varchar(10) |
| trgt_typ_cd | varchar(10) |
| treatmt_dtl | varchar(4000) |
| treatmt_dtl_en | varchar(3000) |
| treatmt_dtl_fr | varchar(3000) |
| treatmt_adnl_dtl | varchar(8000) |
| effectdate | varchar(10) |

## Related Tables

- `new_bucketed_table`
- `ods_hist_latestrec`
- `ods_hist_latestrec_kc`
- `ods_mr_hist`
- `parquet_campaign_offers`
- `temp_client_table`
