# Metric Logic Reference: Wallet Provisioning Success

## Data Access Note

This data is **not available in Hive/EDL**. Access is via direct EDW connection through PySpark using `EDW.cursor()`.

---

## Source Tables

| Schema | Table |
|--------|-------|
| `DDWV05` | `CLNT_CRD_POS_LOG` |
| `DL_DECMAN` | `TOKEN_LIST` |

---

## Code

```python
# PULL TOKEN ID FOR WALLET PROVISIONING / SAVE IN HDFS FOR JOIN WITH PYSPARK

# Create a cursor
cursor = EDW.cursor()

# SQL query to select all columns from the token list table
query = """
SELECT DISTINCT
    SUBSTR(B.CLNT_CRD_NO, 7, 9) AS CLNT_NO,
    B.TXN_DT
FROM DDWV05.CLNT_CRD_POS_LOG AS B
INNER JOIN DL_DECMAN.TOKEN_LIST C
    ON B.TOKN_REQSTR_ID = C.TOKEN_ID
WHERE B.AMT1 = 0
    AND SUBSTR(B.CLNT_CRD_NO, 1, 5) = '45190'
    AND SUBSTR(B.VISA_DR_CRD_NO, 1, 5) = '45199'
    AND SUBSTR(B.TOKN_REQSTR_ID, 1, 1) > '0'
    AND B.POS_ENTR_MODE_CD_NON_EMV = '000'
    AND B.SRVC_CD = 36
    AND C.TOKEN_WALLET_IND = 'Y'
ORDER BY 1
"""

# Execute the query
cursor.execute(query)

# Fetch all results
results = cursor.fetchall()

# Get column names
column_names = [desc[0] for desc in cursor.description]

# Create a pandas DataFrame
token_list_df = pd.DataFrame(results, columns=column_names)

# Convert CLNT_NO to integer (this will automatically remove leading zeros)
token_list_df['CLNT_NO'] = token_list_df['CLNT_NO'].astype(int)

# Display the first few rows
print(token_list_df.head())

# Close the cursor
cursor.close()
```

---

## Output

| Field | Description |
|-------|-------------|
| `CLNT_NO` | Client number (extracted via `SUBSTR(B.CLNT_CRD_NO, 7, 9)`) |
| `TXN_DT` | Transaction date |

---

## Conditions

- `B.AMT1 = 0`
- `SUBSTR(B.CLNT_CRD_NO, 1, 5) = '45190'`
- `SUBSTR(B.VISA_DR_CRD_NO, 1, 5) = '45199'`
- `SUBSTR(B.TOKN_REQSTR_ID, 1, 1) > '0'`
- `B.POS_ENTR_MODE_CD_NON_EMV = '000'`
- `B.SRVC_CD = 36`
- `C.TOKEN_WALLET_IND = 'Y'`

---

## Join Key

`B.TOKN_REQSTR_ID = C.TOKEN_ID`

---
---

# Metric Logic Reference: Email Success

## Data Access Note

SAS code accessing Teradata via `%connectsql` / `connection to teradata`.

---

## Source Tables

| Schema | Table |
|--------|-------|
| `DTZV01` | `VENDOR_FEEDBACK_MASTER` |
| `DTZV01` | `VENDOR_FEEDBACK_EVENT` |

---

## Code

```sas
/* STEP 5: EMAIL */
/* 1: GET EMAIL DATA WITH BOTH FLAGS AND EVENT DATES */

proc sql;
    %connectsql;
    CREATE TABLE email_success AS
    SELECT * FROM CONNECTION TO TERADATA(
        SELECT DISTINCT
            FEEDBACK_MASTER.TREATMENT_ID,
            FEEDBACK_MASTER.CLNT_NO,

            /* Binary flags */
            Max(CASE WHEN disposition_cd=1 THEN 1 ELSE 0 END) AS email_sent,
            Max(CASE WHEN disposition_cd=2 THEN 1 ELSE 0 END) AS email_opened,
            Max(CASE WHEN disposition_cd=3 THEN 1 ELSE 0 END) AS email_clicked,
            Max(CASE WHEN disposition_cd=4 THEN 1 ELSE 0 END) AS email_unsubscribed,
            Max(CASE WHEN disposition_cd=5 THEN 1 ELSE 0 END) AS email_hardbounce,

            /* Event dates */
            MAX(CASE WHEN disposition_cd=1 THEN CAST(disposition_dt_tm AS DATE) END) AS email_sent_date,
            MAX(CASE WHEN disposition_cd=2 THEN CAST(disposition_dt_tm AS DATE) END) AS email_opened_date,
            MAX(CASE WHEN disposition_cd=3 THEN CAST(disposition_dt_tm AS DATE) END) AS email_clicked_date,
            MAX(CASE WHEN disposition_cd=4 THEN CAST(disposition_dt_tm AS DATE) END) AS email_unsubscribed_date,
            MAX(CASE WHEN disposition_cd=5 THEN CAST(disposition_dt_tm AS DATE) END) AS email_hardbounce_date

        FROM DTZV01.VENDOR_FEEDBACK_MASTER FEEDBACK_MASTER
        INNER JOIN DTZV01.VENDOR_FEEDBACK_EVENT FEEDBACK_EVENT
            ON FEEDBACK_MASTER.consumer_id_hashed = FEEDBACK_EVENT.consumer_id_hashed
            AND FEEDBACK_MASTER.TREATMENT_ID = FEEDBACK_EVENT.TREATMENT_ID
        AND FEEDBACK_MASTER.TREATMENT_ID IN('20241968LC','20251968LC','2025227SLC')
        GROUP BY 1,2
    );
QUIT;
```

---

## Output

| Field | Description |
|-------|-------------|
| `TREATMENT_ID` | Treatment identifier |
| `CLNT_NO` | Client number |
| `email_sent` | Binary flag (disposition_cd=1) |
| `email_opened` | Binary flag (disposition_cd=2) |
| `email_clicked` | Binary flag (disposition_cd=3) |
| `email_unsubscribed` | Binary flag (disposition_cd=4) |
| `email_hardbounce` | Binary flag (disposition_cd=5) |
| `email_sent_date` | Date of send event |
| `email_opened_date` | Date of open event |
| `email_clicked_date` | Date of click event |
| `email_unsubscribed_date` | Date of unsubscribe event |
| `email_hardbounce_date` | Date of hardbounce event |

---

## Disposition Code Reference

| disposition_cd | Meaning |
|----------------|---------|
| 1 | email_sent |
| 2 | email_opened |
| 3 | email_clicked |
| 4 | email_unsubscribed |
| 5 | email_hardbounce |

---

## Join Keys

- `FEEDBACK_MASTER.consumer_id_hashed = FEEDBACK_EVENT.consumer_id_hashed`
- `FEEDBACK_MASTER.TREATMENT_ID = FEEDBACK_EVENT.TREATMENT_ID`

---

## Filter

- `FEEDBACK_MASTER.TREATMENT_ID IN('20241968LC','20251968LC','2025227SLC')`

---
---

# Metric Logic Reference: Fulfillment Success

## Data Access Note

SAS code accessing Teradata via `%connectsql` / `connection to teradata`.

---

## Source Tables

| Schema | Table |
|--------|-------|
| `DG6V01` | `TACTIC_EVNT_IP_AR_HIST` |

---

## Code

```sas
/* STEP 6: FULFILLMENT */

proc sql;
    %connectsql
    create table fullfilment_success as
    select * from connection to teradata (
        select
            CLNT_NO,
            AMT as fflmnt_amt,
            ADDNL_DATA_DT as fflmnt_dt
        from DG6V01.TACTIC_EVNT_IP_AR_HIST
        where tactic_id like '2025%120'
        order by CLNT_NO
    );
quit;
```

---

## Output

| Field | Description |
|-------|-------------|
| `CLNT_NO` | Client number |
| `fflmnt_amt` | Fulfillment amount (from `AMT`) |
| `fflmnt_dt` | Fulfillment date (from `ADDNL_DATA_DT`) |

---

## Filter

- `tactic_id like '2025%120'`
