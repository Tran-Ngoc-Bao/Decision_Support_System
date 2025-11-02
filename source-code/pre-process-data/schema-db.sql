CREATE TABLE IF NOT EXISTS provinces (
  id bigint PRIMARY KEY,
  name text,
  create_time timestamp DEFAULT now(),
  update_time timestamp DEFAULT now()
);

CREATE TABLE IF NOT EXISTS districts (
  id bigint PRIMARY KEY,
  province_id bigint NOT NULL,
  name text,
  create_time timestamp DEFAULT now(),
  update_time timestamp DEFAULT now(),
  CONSTRAINT fk_districts_province
    FOREIGN KEY (province_id) REFERENCES provinces(id)
);

CREATE TABLE IF NOT EXISTS wards (
  id bigint PRIMARY KEY,
  district_id bigint NOT NULL,
  name text,
  create_time timestamp DEFAULT now(),
  update_time timestamp DEFAULT now(),
  CONSTRAINT fk_wards_district
    FOREIGN KEY (district_id) REFERENCES districts(id)
);

CREATE TABLE IF NOT EXISTS environment (
  id bigserial PRIMARY KEY,
  category text,
  value text,
  create_time timestamp DEFAULT now(),
  update_time timestamp DEFAULT now()
);

CREATE TABLE IF NOT EXISTS house_rent (
  id bigint PRIMARY KEY,
  available boolean,
  published date,
  price double precision,
  acreage double precision,
  address text,
  house_number text,
  street text,
  ward_id bigint,
  latitude double precision,
  longtitude double precision,
  title text,
  phone_number varchar(10),
  create_time timestamp DEFAULT now(),
  update_time timestamp DEFAULT now(),
  CONSTRAINT fk_house_rent_ward
    FOREIGN KEY (ward_id) REFERENCES wards(id)
);

CREATE TABLE IF NOT EXISTS house_rent_environment (
  id bigserial PRIMARY KEY,
  house_rent_id bigint NOT NULL,
  environment_id bigint NOT NULL,
  create_time timestamp DEFAULT now(),
  update_time timestamp DEFAULT now(),
  CONSTRAINT fk_hre_house_rent
    FOREIGN KEY (house_rent_id) REFERENCES house_rent(id),
  CONSTRAINT fk_hre_environment
    FOREIGN KEY (environment_id) REFERENCES environment(id)
);

CREATE TABLE IF NOT EXISTS log_actions (
  id bigserial PRIMARY KEY,
  action text,
  province_id bigint,
  district_id bigint,
  ward_id bigint,
  search_conntent text,
  persons integer,
  price_min double precision,
  price_max double precision,
  acreage_min double precision,
  acreage_max double precision,
  create_time timestamp DEFAULT now(),
  update_time timestamp DEFAULT now(),
  CONSTRAINT fk_log_actions_province
    FOREIGN KEY (province_id) REFERENCES provinces(id),
  CONSTRAINT fk_log_actions_district
    FOREIGN KEY (district_id) REFERENCES districts(id),
  CONSTRAINT fk_log_actions_ward
    FOREIGN KEY (ward_id) REFERENCES wards(id)
);

CREATE TABLE IF NOT EXISTS actions_results (
  id bigserial PRIMARY KEY,
  log_action_id bigint NOT NULL,
  house_rent_id bigint NOT NULL,
  house_rent_order integer,
  create_time timestamp DEFAULT now(),
  update_time timestamp DEFAULT now(),
  CONSTRAINT fk_actions_results_log_action
    FOREIGN KEY (log_action_id) REFERENCES log_actions(id),
  CONSTRAINT fk_actions_results_house_rent
    FOREIGN KEY (house_rent_id) REFERENCES house_rent(id)
);

CREATE INDEX IF NOT EXISTS idx_districts_province_id ON districts(province_id);
CREATE INDEX IF NOT EXISTS idx_wards_district_id ON wards(district_id);
CREATE INDEX IF NOT EXISTS idx_house_rent_ward_id ON house_rent(ward_id);
CREATE INDEX IF NOT EXISTS idx_hre_house_rent_id ON house_rent_environment(house_rent_id);
CREATE INDEX IF NOT EXISTS idx_hre_environment_id ON house_rent_environment(environment_id);
CREATE INDEX IF NOT EXISTS idx_log_actions_province_id ON log_actions(province_id);
CREATE INDEX IF NOT EXISTS idx_log_actions_district_id ON log_actions(district_id);
CREATE INDEX IF NOT EXISTS idx_log_actions_ward_id ON log_actions(ward_id);
CREATE INDEX IF NOT EXISTS idx_actions_results_log_action_id ON actions_results(log_action_id);
CREATE INDEX IF NOT EXISTS idx_actions_results_house_rent_id ON actions_results(house_rent_id);