-- SQL to create the initial tables for the CVN-ClerkBot database.
-- Run this in mysql from CLI (or in phpMyAdmin) prior to running the bot if
-- you have useMySQL=True. The bot expects these tables to exist!

--
-- Database: cvnclerkbot
-- ------------------------------------------------------

--
-- Table structure for table `channels`
--

CREATE TABLE `channels` (
  `ch_name` varchar(255) binary NOT NULL default ''
) ENGINE=InnoDB DEFAULT CHARSET=binary;

CREATE UNIQUE INDEX channels_chan ON channels (ch_name);
