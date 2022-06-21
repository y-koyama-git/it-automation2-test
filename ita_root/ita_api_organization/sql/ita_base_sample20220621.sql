-- OrganizationDB管理
DROP TABLE IF EXISTS `ITA_DB`.`T_COMN_ORGANIZATION_DB_INFO`;
CREATE TABLE IF NOT EXISTS `ITA_DB`.`T_COMN_ORGANIZATION_DB_INFO`
(
    PRIMARY_KEY                     VARCHAR(40),                                -- 主キー
    DB_HOST                         VARCHAR(255),                               -- ホスト
    DB_PORT                         INT,                                        -- ポート
    DB_DATADBASE                    VARCHAR(255),                               -- DB名
    DB_USER                         VARCHAR(255),                               -- ユーザ
    DB_PASSWORD                     VARCHAR(255),                               -- パスワード
    DB_ROOT_PASSWORD                VARCHAR(255),                               -- rootパスワード
    NOTE                            TEXT,                                       -- 備考
    DISUSE_FLAG                     VARCHAR(1)  ,                               -- 廃止フラグ
    LAST_UPDATE_TIMESTAMP           DATETIME(6),                                -- 最終更新日時
    LAST_UPDATE_USER                VARCHAR(40),                                -- 最終更新者
    PRIMARY KEY(PRIMARY_KEY)
)ENGINE = InnoDB, CHARSET = utf8mb4, COLLATE = utf8mb4_bin, ROW_FORMAT=COMPRESSED ,KEY_BLOCK_SIZE=8;

INSERT INTO `ITA_DB`.`T_COMN_ORGANIZATION_DB_INFO` (`PRIMARY_KEY`, `DB_HOST`, `DB_PORT`, `DB_DATADBASE`, `DB_USER`, `DB_PASSWORD`, `DB_ROOT_PASSWORD`, `NOTE`, `DISUSE_FLAG`, `LAST_UPDATE_TIMESTAMP`, `LAST_UPDATE_USER`) VALUES
('03139c8f-d842-4512-b4d1-fc001b3179b8', 'ita-mariadb', 3306, 'ORGDB_COMA', 'ORGUSER_COMA', 'FTCc9w3|<?=wWSO8', 'password', NULL, NULL, NULL, NULL);

DROP DATABASE IF EXISTS `ORGDB_COMA`;
CREATE DATABASE `ORGDB_COMA` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
DROP USER IF EXISTS 'ORGUSER_COMA'@'%';
CREATE USER IF NOT EXISTS 'ORGUSER_COMA'@'%' IDENTIFIED BY 'FTCc9w3|<?=wWSO8';
GRANT ALL PRIVILEGES ON `ORGDB_COMA`.* TO 'ORGUSER_COMA'@'%' WITH GRANT OPTION;

-- WorkspaceDB管理
DROP TABLE IF EXISTS `ORGDB_COMA`.`T_COMN_ORGANIZATION_DB_INFO`;
CREATE TABLE IF NOT EXISTS `ORGDB_COMA`.`T_COMN_WORKSPACE_DB_INFO`
(
    PRIMARY_KEY                     VARCHAR(40),                                -- 主キー
    DB_HOST                         VARCHAR(255),                               -- ホスト
    DB_PORT                         INT,                                        -- ポート
    DB_DATADBASE                    VARCHAR(255),                               -- DB名
    DB_USER                         VARCHAR(255),                               -- ユーザ
    DB_PASSWORD                     VARCHAR(255),                               -- パスワード
    NOTE                            TEXT,                                       -- 備考
    DISUSE_FLAG                     VARCHAR(1)  ,                               -- 廃止フラグ
    LAST_UPDATE_TIMESTAMP           DATETIME(6),                                -- 最終更新日時
    LAST_UPDATE_USER                VARCHAR(40),                                -- 最終更新者
    PRIMARY KEY(PRIMARY_KEY)
)ENGINE = InnoDB, CHARSET = utf8mb4, COLLATE = utf8mb4_bin, ROW_FORMAT=COMPRESSED ,KEY_BLOCK_SIZE=8;
