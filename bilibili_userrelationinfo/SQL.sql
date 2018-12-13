USE bilibili;
CREATE TABLE bilibili.bilibili_userrelation (
  id int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  user1_mid int(20) UNSIGNED NOT NULL,
  user1_name varchar(50) NOT NULL,
  user2_mid int(20) UNSIGNED NOT NULL,
  user2_name varchar(50) NOT NULL,
  status int(11) DEFAULT NULL,
  PRIMARY KEY (id)
)
ENGINE = MYISAM,
AUTO_INCREMENT = 2,
AVG_ROW_LENGTH = 24,
CHARACTER SET gbk,
CHECKSUM = 0,
COLLATE gbk_chinese_ci;