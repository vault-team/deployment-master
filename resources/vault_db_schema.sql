-- MySQL dump 10.14  Distrib 5.5.49-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: vault
-- ------------------------------------------------------
-- Server version	5.5.49-MariaDB-1ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ConsolidationLog`
--

DROP TABLE IF EXISTS `ConsolidationLog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ConsolidationLog` (
  `last_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`last_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ConsolidationLog`
--

LOCK TABLES `ConsolidationLog` WRITE;
/*!40000 ALTER TABLE `ConsolidationLog` DISABLE KEYS */;
/*!40000 ALTER TABLE `ConsolidationLog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `JobQueue`
--

DROP TABLE IF EXISTS `JobQueue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `JobQueue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action` text,
  `status` varchar(45) DEFAULT NULL,
  `last_touch_timestamp` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `connection_id` varchar(45) DEFAULT NULL,
  `query_id` varchar(45) DEFAULT NULL,
  `worker_id` varchar(45) DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
  `tenant_mppdb_id` int(11) DEFAULT NULL,
  `source_mppdb_id` varchar(45) DEFAULT NULL,
  `dest_mppdb_id` varchar(45) DEFAULT NULL,
  `changes_id` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `JobQueue`
--

LOCK TABLES `JobQueue` WRITE;
/*!40000 ALTER TABLE `JobQueue` DISABLE KEYS */;
/*!40000 ALTER TABLE `JobQueue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MPPDB`
--

DROP TABLE IF EXISTS `MPPDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `MPPDB` (
  `mppdb_id` varchar(512) NOT NULL,
  `mppdb_ip` varchar(15) DEFAULT NULL,
  `tenant_mppdb_group_id` int(11) DEFAULT NULL,
  `mppdb_password` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`mppdb_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MPPDB`
--

LOCK TABLES `MPPDB` WRITE;
/*!40000 ALTER TABLE `MPPDB` DISABLE KEYS */;
/*!40000 ALTER TABLE `MPPDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Query`
--

DROP TABLE IF EXISTS `Query`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Query` (
  `id` varchar(255) NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `end_time` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  `command_type` varchar(255) DEFAULT NULL,
  `query_body` text,
  `user_id` int(11) NOT NULL,
  `tenant_mppdb_id` int(11) NOT NULL,
  `query_status` varchar(255) DEFAULT NULL,
  `mppdb_id` varchar(512) NOT NULL,
  `connection_id` varchar(45) DEFAULT NULL,
  `error_message` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Date` (`start_time`,`end_time`),
  KEY `index3` (`query_status`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Query`
--

LOCK TABLES `Query` WRITE;
/*!40000 ALTER TABLE `Query` DISABLE KEYS */;
/*!40000 ALTER TABLE `Query` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TempPerformance`
--

DROP TABLE IF EXISTS `TempPerformance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TempPerformance` (
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tenant_mppdb_group_id` int(11) NOT NULL,
  `value` float DEFAULT NULL,
  PRIMARY KEY (`time`,`tenant_mppdb_group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TempPerformance`
--

LOCK TABLES `TempPerformance` WRITE;
/*!40000 ALTER TABLE `TempPerformance` DISABLE KEYS */;
/*!40000 ALTER TABLE `TempPerformance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TempSlaGuarantee`
--

DROP TABLE IF EXISTS `TempSlaGuarantee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TempSlaGuarantee` (
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tenant_mppdb_group_id` int(11) NOT NULL,
  `value` float DEFAULT NULL,
  PRIMARY KEY (`time`,`tenant_mppdb_group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TempSlaGuarantee`
--

LOCK TABLES `TempSlaGuarantee` WRITE;
/*!40000 ALTER TABLE `TempSlaGuarantee` DISABLE KEYS */;
/*!40000 ALTER TABLE `TempSlaGuarantee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TempTenantMPPDBActivity`
--

DROP TABLE IF EXISTS `TempTenantMPPDBActivity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TempTenantMPPDBActivity` (
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tenant_mppdb_id` int(11) NOT NULL,
  `value` float DEFAULT NULL,
  PRIMARY KEY (`time`,`tenant_mppdb_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TempTenantMPPDBActivity`
--

LOCK TABLES `TempTenantMPPDBActivity` WRITE;
/*!40000 ALTER TABLE `TempTenantMPPDBActivity` DISABLE KEYS */;
/*!40000 ALTER TABLE `TempTenantMPPDBActivity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TenantMPPDB`
--

DROP TABLE IF EXISTS `TenantMPPDB`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TenantMPPDB` (
  `tenant_mppdb_id` int(11) NOT NULL AUTO_INCREMENT,
  `tenant_mppdb_group_id` int(11) DEFAULT NULL,
  `request_node_quantity` int(11) DEFAULT NULL,
  `flavor` varchar(50) DEFAULT NULL,
  `tenant_id` varchar(50) DEFAULT NULL,
  `tenant_mppdb_name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`tenant_mppdb_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TenantMPPDB`
--

LOCK TABLES `TenantMPPDB` WRITE;
/*!40000 ALTER TABLE `TenantMPPDB` DISABLE KEYS */;
/*!40000 ALTER TABLE `TenantMPPDB` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TenantMPPDBGroup`
--

DROP TABLE IF EXISTS `TenantMPPDBGroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TenantMPPDBGroup` (
  `tenant_mppdb_group_id` int(11) NOT NULL AUTO_INCREMENT,
  `group_size` int(11) DEFAULT NULL,
  `formation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  `node_quantity` int(11) DEFAULT NULL,
  `flavor` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`tenant_mppdb_group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TenantMPPDBGroup`
--

LOCK TABLES `TenantMPPDBGroup` WRITE;
/*!40000 ALTER TABLE `TenantMPPDBGroup` DISABLE KEYS */;
/*!40000 ALTER TABLE `TenantMPPDBGroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `User`
--

DROP TABLE IF EXISTS `User`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `User` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(255) DEFAULT NULL,
  `user_role` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `tenant_mppdb_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `index2` (`tenant_mppdb_id`,`user_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `User`
--

LOCK TABLES `User` WRITE;
/*!40000 ALTER TABLE `User` DISABLE KEYS */;
/*!40000 ALTER TABLE `User` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-11-15 17:55:14
