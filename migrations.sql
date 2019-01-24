USE pynformatics;
ALTER TABLE runs add COLUMN source_hash varchar(32);
ALTER TABLE runs add COLUMN ejudge_url varchar(50);