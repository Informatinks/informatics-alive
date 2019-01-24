USE pynformatics;
ALTER TABLE runs add COLUMN source_hash varchar(32);
ALTER TABLE runs add COLUMN ejudge_url varchar(50);

USE ejudge;
ALTER TABLE mdl_run_comments ADD COLUMN py_run_id INTEGER;
UPDATE mdl_run_comments AS cmt INNER JOIN (
    SELECT id, ej_run_id, ej_contest_id FROM pynformatics.runs
) AS run
ON run.ej_contest_id = cmt.contest_id AND run.ej_run_id = cmt.run_id
SET cmt.py_run_id =run.id;
