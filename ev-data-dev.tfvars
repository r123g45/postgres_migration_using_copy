env_name = "dev"

# VPC
# primary region - us-east-2
vpc_id = "vpc-04fcf1df8f1e80323"
subnet_ids = [
  "subnet-0b0668efce715e224",
  "subnet-0b424a65681c17865"
]
# secondary region - us-east-1
secondary_vpc_id = "vpc-0ad65b4c984b5c3bc"
secondary_subnet_ids = [
  "subnet-04a7eadcef00d45d8",
  "subnet-0249f29fed435d4b9"
]

# KMS
kms_key_tags = {
  "evtech:bu"      = "core",
  "evtech:owner"   = "cloudops@eagleview.com",
  "evtech:program" = "shared-databases"
}

# RDS
rds_configmap = {
  "poc-cluster" = {
    instance_class                 = "db.r5.large",
    engine_version                 = "12.4",
    skip_cmk_usage                 = false,
    enable_cpu_autoscaling         = true,
    cpu_target_value               = 55,
    enable_connections_autoscaling = true,
    connections_target_value       = 123,
    multi_region_deployment        = false,
    allowed_connection = [
      # "10.228.16.0/20", # CI AWS account access
      # "10.230.12.0/22",  # ev-data DMS access
      # "10.243.0.0/16" # ev-platform-dev
      "10.0.0.0/8",     # ev internal access
      "172.23.160.0/20" #corp cidr is different
    ],
    databases = [
    ],
    db_parameters_family = "aurora-postgresql12",
    tags = {
      "evtech:bu"      = "construction",
      "evtech:owner"   = "cloudops@eagleview.com",
      "evtech:program" = "shared-databases"
    }
  },
  "con-cluster" = {
    instance_class = "db.r6g.large",
    engine_version = "12.4",
    skip_cmk_usage = true,
    allowed_connection = [
      # "10.228.16.0/20", # CI AWS account access
      # "10.230.12.0/22",  # ev-data DMS access
      # "10.243.0.0/16" # ev-platform-dev
      "10.0.0.0/8",     # ev internal access
      "172.23.160.0/20" #corp cidr is different
    ],
    databases = [
      {
        db_name = "object_storage",
        users = {
          "evoss_owner" = "rw"
        },
        schemas = [
          "public"
        ],
        extensions = []
      },
      {
        db_name = "graph",
        users = {
          "graph_owner"  = "rw",
          "graph_reader" = "ro"
        },
        schemas = [
          "boundary",
          "graph",
          "graph_asset_geohash_partitions",
          "graph_asset_id_partitions",
          "migrate_parcels_bo",
          "migrate_parcels_parcels",
          "sqitch",
          "public"
        ],
        extensions = [
          "plpgsql",
          "postgis",
          "uuid-ossp"
        ]
      },
      {
        db_name = "factory-dx-services",
        users = {
          "factory_dx_services_owner"  = "rw",
          "factory_dx_services_reader" = "ro"
        },
        schemas = [
          "public",
          "dx-triage",
          "dx-qc-backend"
        ],
        extensions = []
      },
      {
        db_name = "dbDrupal",
        users = {
          "dbDrupal_owner" = "rw"
        },
        schemas = [
          "public"
        ],
        extensions = [
          "pg_trgm"
        ]
      }
    ],
    db_parameters_family = "aurora-postgresql12",
    db_cluster_parameters = {
      "rds.logical_replication" = "1"
    },
    db_parameters = {
      "shared_preload_libraries"            = "auto_explain,pg_stat_statements,pg_hint_plan,pgaudit",
      "log_statement"                       = "ddl",
      "log_connections"                     = "1",
      "log_disconnections"                  = "1",
      "log_lock_waits"                      = "1",
      "log_min_duration_statement"          = "1000",
      "auto_explain.log_min_duration"       = "5000",
      "auto_explain.log_verbose"            = "1",
      "log_rotation_age"                    = "1440",
      "log_rotation_size"                   = "102400",
      "rds.log_retention_period"            = "10080",
      "random_page_cost"                    = "1",
      "track_activity_query_size"           = "32768",
      "track_functions"                     = "all",
      "idle_in_transaction_session_timeout" = "7200000",
      "statement_timeout"                   = "7200000",
      "search_path"                         = "graph,public",
      "max_locks_per_transaction"           = "1024"
    },
    tags = {
      "evtech:bu"      = "construction",
      "evtech:owner"   = "cloudops@eagleview.com",
      "evtech:program" = "shared-databases"
    }
  },
  "ins-cluster" = {
    instance_class = "db.r6g.large",
    engine_version = "12.4",
    skip_cmk_usage = true,
    allowed_connection = [
      "10.0.0.0/8",     # ev internal access
      "172.23.160.0/20" #corp cidr is different
    ],
    databases = [
      {
        db_name = "onondaga",
        users = {
          "onondaga_owner" = "rw"
        },
        schemas = [
          "onondaga"
        ],
        extensions = [
          "plpgsql"
        ]
      },
      {
        db_name = "weather_cache",
        users = {
          "weather_cache_owner" = "rw"
        },
        schemas = [
          "public"
        ],
        extensions = []
      },
      {
        db_name = "vendor",
        users = {
          "vendor_owner" = "rw"
        },
        schemas = [
          "public",
          "information_schema"
        ],
        extensions = []
      },
      {
        db_name = "onsite_capture_solution",
        users = {
          "onsite_capture_solution_owner" = "rw"
        },
        schemas = [
          "public"
        ],
        extensions = []
      }
    ],
    db_parameters_family = "aurora-postgresql12",
    tags = {
      "evtech:bu"      = "insurance",
      "evtech:owner"   = "cloudops@eagleview.com",
      "evtech:program" = "shared-databases"
    }
  },
  "gov-cluster" = {
    instance_class = "db.r6g.large",
    engine_version = "12.4",
    skip_cmk_usage = true,
    allowed_connection = [
      "10.0.0.0/8",     # ev internal access
      "172.23.160.0/20" #corp cidr is different
    ],
    databases = [
      {
        db_name = "ipui_dev",
        users = {
          "ipui_dev_owner" = "rw"
        },
        schemas = [
          "postmarianas",
          "public"
        ],
        extensions = [
          "plpgsql",
          "postgis",
          "postgres_fdw",
          "sslinfo"
        ]
      },
      {
        db_name = "ipui_dev_archive",
        users = {
          "ipui_dev_archive_owner" = "rw"
        },
        schemas = [
          "public"
        ],
        extensions = [
          "plpgsql"
        ]
      }
    ],
    db_parameters_family = "aurora-postgresql12",
    tags = {
      "evtech:bu"      = "government",
      "evtech:owner"   = "cloudops@eagleview.com",
      "evtech:program" = "shared-databases"
    }
  },
  "imws-cluster" = {
    instance_class         = "db.r6g.4xlarge",
    engine_version         = "12.4",
    enable_cpu_autoscaling = true,
    cpu_target_value       = "75",
    allowed_connection = [
      # "10.228.16.0/20", # CI AWS account access
      # "10.230.12.0/22",  # ev-data DMS access
      # "10.243.0.0/16", # ev-platform-dev
      "10.0.0.0/8" # ev internal access
    ],
    databases = [
      {
        db_name = "metadata_service",
        users = {
          "metadata_owner" = "rw"
        },
        schemas = [
          "public"
        ],
        extensions = [
          "postgis",
          "plpgsql"
        ]
      }
    ],
    db_parameters_family = "aurora-postgresql12",
    db_cluster_parameters = {
      "rds.force_ssl" = "1"
    },
    db_parameters = {
      "shared_preload_libraries"            = "auto_explain,pg_stat_statements,pg_hint_plan,pgaudit",
      "log_statement"                       = "ddl",
      "log_connections"                     = "1",
      "log_disconnections"                  = "1",
      "log_lock_waits"                      = "1",
      "log_min_duration_statement"          = "5000",
      "auto_explain.log_min_duration"       = "5000",
      "auto_explain.log_verbose"            = "1",
      "log_rotation_age"                    = "1440",
      "log_rotation_size"                   = "102400",
      "rds.log_retention_period"            = "10080",
      "random_page_cost"                    = "1",
      "track_activity_query_size"           = "16384",
      "idle_in_transaction_session_timeout" = "7200000",
      "statement_timeout"                   = "7200000",
      "search_path"                         = "\"$user\",public"
    },
    tags = {
      "evtech:bu"      = "government",
      "evtech:owner"   = "cloudops@eagleview.com",
      "evtech:program" = "shared-databases"
    }
  },
  # Managed by graph team
  "graph-cluster" = {
    instance_class     = "db.r6g.large",
    engine_version     = "11.9",
    managed_by_ansible = false,
    allowed_connection = [
      # "10.228.16.0/20", # CI AWS account access
      # "10.230.12.0/22",  # ev-data DMS access
      # "10.243.0.0/16" # ev-platform-dev
      "10.0.0.0/8",     # ev internal access
      "172.23.160.0/20" #corp cidr is different
    ],
    master_db_name       = "graph",
    master_username      = "graph_master",
    db_parameters_family = "aurora-postgresql11",
    db_cluster_parameters = {
      "rds.force_ssl"           = "0",
      "rds.logical_replication" = "0",
      "synchronous_commit"      = "on",
      "timezone"                = "UTC"
    },
    db_parameters = {
      "log_statement"                       = "ddl",
      "log_connections"                     = "1",
      "log_disconnections"                  = "1",
      "log_lock_waits"                      = "1",
      "log_min_duration_statement"          = "1000",
      "auto_explain.log_min_duration"       = "5000",
      "auto_explain.log_verbose"            = "1",
      "log_rotation_age"                    = "1440",
      "log_rotation_size"                   = "102400",
      "rds.log_retention_period"            = "10080",
      "random_page_cost"                    = "1",
      "track_activity_query_size"           = "32768",
      "track_functions"                     = "all",
      "idle_in_transaction_session_timeout" = "7200000",
      "statement_timeout"                   = "7200000",
      "search_path"                         = "graph,public",
      "max_locks_per_transaction"           = "1024"
    },
    tags = {
      "evtech:bu"      = "government",
      "evtech:owner"   = "cloudops@eagleview.com",
      "evtech:program" = "shared-databases"
    }
  },
  "testing-cluster" = {
    instance_class = "db.r5.large",
    engine_version = "12.4",
    allowed_connection = [
      # "10.228.16.0/20", # CI AWS account access
      # "10.230.12.0/22",  # ev-data DMS access
      # "10.243.0.0/16", # ev-platform-dev
      "10.0.0.0/8" # ev internal access
    ],
    databases = [
      {
        db_name = "northface",
        users = {
          "northface_owner" = "rw",
          "owner"           = "ro",
          "northface_admin" = "rw"
        },
        schemas = [
          "public",
          "my_new_topo",
          "tiger",
          "tiger_data",
          "topology"
        ],
        extensions = [
          "fuzzystrmatch",
          "plpgsql",
          "postgis",
          "postgis_tiger_geocoder",
          "postgis_topology"
        ]
      },
      {
        db_name = "northface-testing",
        users = {
          "northface_owner" = "rw",
          "owner"           = "ro",
          "northface_admin" = "rw"
        },
        schemas = [
          "public",
          "my_new_topo",
          "tiger",
          "tiger_data",
          "topology"
        ],
        extensions = [
          "fuzzystrmatch",
          "plpgsql",
          "postgis",
          "postgis_tiger_geocoder",
          "postgis_topology"
        ]
      }
    ],
    db_parameters_family = "aurora-postgresql12",
    db_cluster_parameters = {
      "rds.force_ssl" = "1"
    },
    db_parameters = {
      "shared_preload_libraries"            = "auto_explain,pg_stat_statements,pg_hint_plan,pgaudit",
      "log_statement"                       = "ddl",
      "log_connections"                     = "1",
      "log_disconnections"                  = "1",
      "log_lock_waits"                      = "1",
      "log_min_duration_statement"          = "5000",
      "auto_explain.log_min_duration"       = "5000",
      "auto_explain.log_verbose"            = "1",
      "log_rotation_age"                    = "1440",
      "log_rotation_size"                   = "102400",
      "rds.log_retention_period"            = "10080",
      "random_page_cost"                    = "1",
      "track_activity_query_size"           = "16384",
      "idle_in_transaction_session_timeout" = "7200000",
      "statement_timeout"                   = "7200000",
      "search_path"                         = "\"$user\",public"
    },
    tags = {
      "evtech:bu"            = "core",
      "evtech:owner"         = "cloudops@eagleview.com",
      "evtech:program"       = "shared-databases"
      "evtech:testing_owner" = "Rahul"
    }
  }
}
