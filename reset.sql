SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
where datname = 'game_of_thrones';
DROP DATABASE game_of_thrones;
CREATE DATABASE game_of_thrones;