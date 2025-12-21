-- For authentication test
CREATE USER 'native_user'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'native_user'@'%' WITH GRANT OPTION;

CREATE USER 'sha2_user'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'sha2_user'@'%' WITH GRANT OPTION;

FLUSH PRIVILEGES;
