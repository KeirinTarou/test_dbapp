DROP TABLE IF EXISTS Questions;
DROP TABLE IF EXISTS Sections;
DROP TABLE IF EXISTS Chapters;

CREATE TABLE Chapters (
    ChapterNumber INTEGER NOT NULL
    , ChapterTitle TEXT NOT NULL
    , ChapterDescription TEXT DEFAULT NULL
    , PRIMARY KEY (ChapterNumber)   
);

CREATE TABLE Sections (
    SectionNumber INTEGER NOT NULL
    , ChapterNumber INTEGER NOT NULL
    , SectionTitle TEXT NOT NULL
    , SectionDescription TEXT DEFAULT NULL
    , PRIMARY KEY (ChapterNumber, SectionNumber)
    , FOREIGN KEY (ChapterNumber) 
        REFERENCES Chapters(ChapterNumber)
        ON DELETE CASCADE
);

CREATE TABLE Questions (
    ChapterNumber INTEGER NOT NULL
    , SectionNumber INTEGER NOT NULL
    , QuestionNumber INTEGER NOT NULL
    , Question TEXT NOT NULL
    , AnswerQuery TEXT NOT NULL
    , CheckMode TEXT NOT NULL 
    , PRIMARY KEY (ChapterNumber, SectionNumber, QuestionNumber)
    , FOREIGN KEY (ChapterNumber) 
        REFERENCES Chapters(ChapterNumber)
        ON DELETE CASCADE
    , FOREIGN KEY (ChapterNumber, SectionNumber)
        REFERENCES Sections(ChapterNumber, SectionNumber)
        ON DELETE CASCADE
);
