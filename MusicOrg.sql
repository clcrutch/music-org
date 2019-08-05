IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'MusicOrg')
    BEGIN
        CREATE DATABASE [MusicOrg]
    END;
GO

USE MusicOrg
GO

IF NOT EXISTS (SELECT * from sysobjects WHERE NAME='Music' and xtype='U')
    CREATE TABLE Music (
        ID INT IDENTITY PRIMARY KEY,
        FilePath NVARCHAR(MAX) NOT NULL,
        Length FLOAT NOT NULL,
        FingerPrint VARBINARY(MAX) NOT NULL,
        MusicBrainzID NVARCHAR(256) NULL,
        Title NVARCHAR(256) NULL,
        AlbumID INT NULL,
        Track INT NULL,
        Genre NVARCHAR(256) NULL,
        Lyrics NVARCHAR(MAX) NULL
    )

IF NOT EXISTS (SELECT * from sysobjects WHERE NAME='Albums' and xtype='U')
    CREATE TABLE Albums (
        ID INT IDENTITY PRIMARY KEY,
        MusicBrainzID NVARCHAR(256) NULL,
        Name NVARCHAR(256) NOT NULL,
        Date DATE NULL,
        CoverArt VARBINARY(MAX) NULL,
        MimeType NVARCHAR(64) NULL
    )

IF NOT EXISTS (SELECT * from sysobjects WHERE NAME='Artists' and xtype='U')
    CREATE TABLE Artists (
        ID INT IDENTITY PRIMARY KEY,
        MusicBrainzID NVARCHAR(256) NULL,
        Name NVARCHAR(256) NOT NULL,
    )

IF NOT EXISTS (SELECT * from sysobjects WHERE NAME='ArtistMusicMap' and xtype='U')
    CREATE TABLE ArtistMusicMap (
        ID INT IDENTITY PRIMARY KEY,
        MusicID INT NOT NULL,
        ArtistID INT NOT NULL
    )

IF NOT EXISTS (SELECT * from sysobjects WHERE NAME='PossibleMatches' and xtype='U')
    CREATE TABLE PossibleMatches (
        ID INT IDENTITY PRIMARY KEY,
        MusicID INT NOT NULL,
        Artist NVARCHAR(256) NOT NULL,
        Title NVARCHAR(256) NOT NULL,
        MusicBrainzID NVARCHAR(256) NOT NULL
    )

IF NOT EXISTS (SELECT * from sysobjects WHERE NAME='OriginalFiles' and xtype='U')
    CREATE TABLE OriginalFiles (
        ID INT IDENTITY PRIMARY KEY,
        MusicID INT NOT NULL,
        OriginalFilePath NVARCHAR(MAX) NOT NULL
    )

IF NOT EXISTS (SELECT * from sysobjects WHERE NAME='Steps' and xtype='U')
    CREATE TABLE Steps (
        ID INT IDENTITY PRIMARY KEY,
        MusicID INT NOT NULL,
        StepName NVARCHAR(64) NOT NULL
    )
GO

CREATE OR ALTER PROCEDURE sp_InsertLastStep
    @FilePath NVARCHAR(MAX),
    @StepName NVARCHAR(64)
AS
    DECLARE @MusicID INT
    SELECT @MusicID = ID FROM Music WHERE FilePath = @FilePath
    INSERT INTO Steps (MusicID, StepName) VALUES (@MusicID, @StepName)
GO

CREATE OR ALTER PROCEDURE sp_SelectSteps
    @FilePath NVARCHAR(MAX)
AS
    SELECT StepName
    FROM Steps s
    JOIN Music m on m.ID = s.MusicID
    WHERE m.FilePath = @FilePath
    ORDER BY s.ID DESC
GO

CREATE OR ALTER PROCEDURE sp_InsertFile
    @FilePath NVARCHAR(MAX),
    @Length FLOAT,
    @Fingerprint VARBINARY(MAX)
AS
    INSERT INTO Music (FilePath, Length, Fingerprint) VALUES (@FilePath, @Length, @Fingerprint);
    INSERT INTO OriginalFiles (MusicID, OriginalFilePath) VALUES (SCOPE_IDENTITY(), @FilePath)
GO

CREATE OR ALTER PROCEDURE sp_SelectFileFingerprintLength
    @FilePath NVARCHAR(MAX)
AS
    SELECT Length, Fingerprint FROM Music WHERE FilePath = @FilePath
GO

CREATE OR ALTER PROCEDURE sp_InsertPossibleMatches
    @FilePath NVARCHAR(MAX),
    @Artist NVARCHAR(256),
    @Title NVARCHAR(256),
    @MusicBrainzID NVARCHAR(256)
AS
    DECLARE @MusicID INT
    SELECT @MusicID = ID FROM Music WHERE FilePath = @FilePath
    INSERT PossibleMatches (MusicID, Artist, Title, MusicBrainzID) VALUES (@MusicID, @Artist, @Title, @MusicBrainzID)
GO

CREATE OR ALTER PROCEDURE sp_SelectPossibleMatches
    @FilePath NVARCHAR(MAX)
AS
    SELECT pm.Artist, pm.Title, pm.MusicBrainzID
    FROM PossibleMatches pm
    JOIN Music m on m.ID = pm.MusicID
    WHERE m.FilePath = @FilePath
GO

CREATE OR ALTER PROCEDURE sp_InsertIntoArtists
    @MusicBrainzID NVARCHAR(256),
    @ArtistName NVARCHAR(256),
    @FilePath NVARCHAR(MAX)

AS
    IF NOT EXISTS(SELECT * FROM Artists WHERE MusicBrainzID = @MusicBrainzID)
        INSERT INTO Artists (MusicBrainzID, Name) VALUES (@MusicBrainzID, @ArtistName)
    DECLARE @ArtistID INT
    DECLARE @MusicID INT
    SELECT @ArtistID = ID FROM Artists WHERE MusicBrainzID = @MusicBrainzID
    SELECT @MusicID = ID FROM Music WHERE FilePath = @FilePath
    INSERT INTO ArtistMusicMap (MusicID, ArtistID) VALUES (@MusicID, @ArtistID)
GO

CREATE OR ALTER PROCEDURE sp_UpdateMusic
    @AlbumMusicBrainzID NVARCHAR(256),
    @AlbumName NVARCHAR(256),
    @AlbumYear DATE,
    @AlbumCoverArt VARBINARY(MAX),
    @AlbumMimeType NVARCHAR(MAX),
    @SongMusicBrainzID NVARCHAR(256),
    @SongTitle NVARCHAR(256),
    @SongTrackNumber SMALLINT,
    @SongGenre NVARCHAR(256),
    @FilePath NVARCHAR(MAX)
AS
    IF NOT EXISTS(SELECT * FROM Albums WHERE MusicBrainzID = @AlbumMusicBrainzID)
        INSERT INTO Albums (MusicBrainzID, Name, Date, CoverArt, MimeType) VALUES (@AlbumMusicBrainzID, @AlbumName, @AlbumYear, @AlbumCoverArt, @AlbumMimeType)
    DECLARE @AlbumID INT
    SELECT @AlbumID = ID FROM Albums WHERE MusicBrainzID = @AlbumMusicBrainzID
    UPDATE Music
    SET MusicBrainzID = @SongMusicBrainzID,
        Title = @SongTitle,
        AlbumID = @AlbumID,
        Track = @SongTrackNumber,
        Genre = @SongGenre
    WHERE FilePath = @FilePath
GO

CREATE OR ALTER PROCEDURE sp_SelectSongTags
    @FilePath NVARCHAR(MAX)
AS
    SELECT art.Name,
        alb.Name,
        alb.Date,
        alb.CoverArt,
        alb.MimeType,
        m.Genre,
        m.Track,
        m.Title
    FROM Music m
    JOIN ArtistMusicMap amm ON amm.MusicID = m.ID
    JOIN Artists art ON art.ID = amm.ArtistID 
    JOIN Albums alb ON alb.ID = m.AlbumID
    WHERE m.FilePath = @FilePath
GO

CREATE OR ALTER PROCEDURE sp_UpdateSongTags
    @ArtistName NVARCHAR(256),
    @AlbumName NVARCHAR(256),
    @AlbumDate NVARCHAR(256),
    @AlbumCoverArt VARBINARY(MAX),
    @AlbumMimeType NVARCHAR(64),
    @Gnere NVARCHAR(256),
    @TrackNumber SMALLINT,
    @Title NVARCHAR(256),
    @FilePath NVARCHAR(MAX)
AS
    IF NOT EXISTS(SELECT * FROM Artists WHERE Name = @ArtistName)
        INSERT INTO Artists (Name) VALUES (@ArtistName)
    DECLARE @ArtistID INT
    SELECT @ArtistID = ID FROM Artists WHERE Name = @ArtistName

    IF NOT EXISTS(SELECT * FROM Albums WHERE Name = @AlbumName)
        INSERT INTO Albums (Name, Date, CoverArt, MimeType) VALUES (@AlbumName, @AlbumDate, @AlbumCoverArt, @AlbumMimeType)
    DECLARE @AlbumID INT;
    SELECT @AlbumID = ID FROM Albums WHERE Name = @AlbumName

    DECLARE @MusicID INT
    SELECT @MusicID = ID FROM Music WHERE FilePath = @FilePath

    UPDATE Music
    SET AlbumID = @AlbumID,
        Genre = @Gnere,
        Track = @TrackNumber,
        Title = @Title
    WHERE FilePath = @FilePath

    IF EXISTS(
        SELECT * FROM ArtistMusicMap amm
        JOIN Music m on m.ID = amm.MusicID
        WHERE m.FilePath = @FilePath
    )
        UPDATE amm
        SET ArtistID = @ArtistID
        FROM ArtistMusicMap amm
        JOIN Music m on m.ID = amm.MusicID
        WHERE m.FilePath = @FilePath
    ELSE
        INSERT INTO ArtistMusicMap (MusicID, ArtistID) VALUES (@MusicID, @ArtistID)
GO

CREATE OR ALTER PROCEDURE sp_SelectSongTitleArtist
    @FilePath NVARCHAR(MAX)
AS
    SELECT m.Title,
            art.Name
    FROM Music m
    JOIN ArtistMusicMap amm ON amm.MusicID = m.ID
    JOIN Artists art ON art.ID = amm.ArtistID
    WHERE m.FilePath = @FilePath
GO

CREATE OR ALTER PROCEDURE sp_UpdateSongLyrics
    @Lyrics NVARCHAR(MAX),
    @FilePath NVARCHAR(MAX)
AS
    UPDATE Music
    SET Lyrics = @Lyrics
    WHERE FilePath = @FilePath
GO

CREATE OR ALTER PROCEDURE sp_SelectSongLocationInfo
    @FilePath NVARCHAR(MAX)
AS
    SELECT art.Name,
        alb.Name,
        m.Track,
        m.Title
    FROM Music m
    JOIN ArtistMusicMap amm ON amm.MusicID = m.ID
    JOIN Artists art ON art.ID = amm.ArtistID
    JOIN Albums alb ON alb.ID = m.AlbumID
    WHERE m.FilePath = @FilePath
GO

CREATE OR ALTER PROCEDURE sp_SelectLyrics
    @FilePath NVARCHAR(MAX)
AS
    SELECT Lyrics
    FROM Music
    WHERE FilePath = @FilePath
GO

CREATE OR ALTER PROCEDURE sp_UpdatePath
    @OriginalPath NVARCHAR(MAX),
    @NewFilePath NVARCHAR(MAX)
AS
    UPDATE Music
    SET FilePath = @NewFilePath
    WHERE FilePath = @OriginalPath
GO
