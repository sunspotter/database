CREATE TABLE user (
	id INTEGER NOT NULL,
	username VARCHAR,
	PRIMARY KEY (id)
);

CREATE TABLE fitsfiles (
	id INTEGER NOT NULL,
	filename VARCHAR,
	obs_date DATETIME,
	PRIMARY KEY (id)
);

CREATE TABLE images (
	id INTEGER NOT NULL,
	filename VARCHAR,
	zooniverse_id VARCHAR,
	area FLOAT,
	areafrac FLOAT,
	areathesh VARCHAR,
	arid INTEGER,
	bipolesep FLOAT,
	bmax FLOAT,
	c1flr12hr BOOLEAN,
	c1flr24hr BOOLEAN,
	c5flr12hr BOOLEAN,
	c5flr24hr BOOLEAN,
	deg2dc FLOAT,
	detstatus INTEGER,
	id_filename INTEGER,
	flux FLOAT,
	fluxfrac FLOAT,
	hcpos_x FLOAT,
	hcpos_y FLOAT,
	m1flr12hr BOOLEAN,
	m1flr24hr BOOLEAN,
	m5flr12hr BOOLEAN,
	m5flr24hr BOOLEAN,
	magstatus INTEGER,
	npsl INTEGER,
	posstatus INTEGER,
	pslcurvature FLOAT,
	psllength FLOAT,
	pxpos_x FLOAT,
	pxpos_y FLOAT,
	pxscl_hpc2stg FLOAT,
	rvalue FLOAT,
	sszn INTEGER,
	sszstatus INTEGER,
	wlsg FLOAT,
	PRIMARY KEY (id),
	CHECK (c1flr12hr IN (0, 1)),
	CHECK (c1flr24hr IN (0, 1)),
	CHECK (c5flr12hr IN (0, 1)),
	CHECK (c5flr24hr IN (0, 1)),
	FOREIGN KEY(id_filename) REFERENCES fitsfiles (id),
	CHECK (m1flr12hr IN (0, 1)),
	CHECK (m1flr24hr IN (0, 1)),
	CHECK (m5flr12hr IN (0, 1)),
	CHECK (m5flr24hr IN (0, 1))
);

CREATE TABLE classification (
	id INTEGER NOT NULL,
	zooniverse_class VARCHAR,
	user_id INTEGER,
	image_id_0 INTEGER,
	image_id_1 INTEGER,
	image0_more_complex_image1 BOOLEAN,
	used_inverted BOOLEAN,
	date_created DATETIME,
	date_started DATETIME,
	date_finished DATETIME,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES user (id),
	FOREIGN KEY(image_id_0) REFERENCES images (id),
	FOREIGN KEY(image_id_1) REFERENCES images (id),
	CHECK (image0_more_complex_image1 IN (0, 1)),
	CHECK (used_inverted IN (0, 1))
);

CREATE TABLE zoorank (
	id INTEGER NOT NULL,
	image_id INTEGER,
	count INTEGER,
	k_value INTEGER,
	score FLOAT,
	std_dev FLOAT,
	PRIMARY KEY (id),
	FOREIGN KEY(image_id) REFERENCES images (id)
);

.mode csv
.separator ";"
.import lookup_users.csv user
.import lookup_timesfits.csv fitsfiles
.import lookup_properties.csv images
.import classifications_noRepeated.csv classification
.import rankings.csv zoorank

CREATE UNIQUE INDEX "idx_images_id" ON "images" ("id" ASC);
CREATE UNIQUE INDEX "idx_zoorank_image_id" ON "zoorank" ("image_id" ASC);
CREATE INDEX "idx_zoorank_score_desc" ON "zoorank" ("score" DESC);
