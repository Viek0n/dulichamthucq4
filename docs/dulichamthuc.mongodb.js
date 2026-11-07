const dulichamthuc = db.getSiblingDB("dulichamthuc");

//POI
dulichamthuc.createCollection("POI", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "slug",
        "name",
        'address',
        "open_at",
        "close_at",
        "contact",
        "image",
        "latitude",
        "longitude",
        "trigger_radius",
        "is_delete",
        "poi_owner_id"
      ],
      properties: {
        slug: {
            bsonType: "string",
            description: "đặt kiểu com-que-duong-bau hỗ trợ tìm kiếm và hiển thị url"
        },
        name: {
            bsonType: "string",
            description: "tên"
        },
        address: {
            bsonType: "string",
            description: "địa chỉ"
        },
        open_at:{
            bsonType: "string",
            description: "giờ mở cửa"
        },
        close_at:{
            bsonType: "string",
            description: "giờ đóng cửa"
        },
        contact:{
            bsonType: "string",
            description: "số điện thoại"
        },
        image:{
            bsonType: "string",
            description: "đường dẫn ảnh"
        },
        latitude: {
            bsonType: "double",
            description: "vĩ độ"
        },
        longitude: {
            bsonType: "double",
            description: "kinh độ"
        },
        trigger_radius: {
            bsonType: "double",
            minimum: 0,
            description: "phạm vi hoạt động của poi"
        },
        is_delete: {
            bsonType: "bool",
            description: "soft delete lock"
        },
        poi_owner_id: {
            bsonType: "objectId",
            description: "khóa ngoại tới admin_users"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});
dulichamthuc.POI.createIndex({ slug: 1 }, { unique: true });
dulichamthuc.POI.createIndex({ latitude: 1, longitude: 1 });

// Menu item
dulichamthuc.createCollection("menu_items", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "poi_id",
        "name",
        "price"
      ],
      properties: {
        poi_id:{
            bsonType: "objectId",
            description: "khóa ngoại tới POI"
        },
        name:{
            bsonType: "string",
            description: "tên món"
        },
        price:{
            bsonType: "int",
            description: "giá món(vnđ)"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});

// Submission
dulichamthuc.createCollection("poi_submissions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "slug",
        "proposed_change",
        "submiss_at",
        "review_status",
        "admin_note",
        "for_poi",
        "submissed_by"
      ],
      properties: {
        slug:{
            bsonType: "string",
            description: "đặt kiểu poi-01 hỗ trợ tìm kiếm và hiển thị url"
        },
        proposed_change: {
            bsonType: "object",
            description: "lưu tạm đối tượng"
        },
        submiss_at:{
            bsonType: "date",
            description: "tạo yêu cầu lúc"
        },
        review_status:{
            bsonType: "string",
            enum : [
                "PENDING",
                "ACCEPTED",
                "REJECTED"
            ],
            description: "trạng thái xử lý yêu cầu"
        },
        admin_note:{
            bsonType: "string",
            description: "nhận xét của qtv"
        },
        for_poi:{
            bsonType: "objectId",
            description: "khóa ngoại tới POI"
        },
        submissed_by:{
            bsonType: "objectId",
            description: "khóa ngoại tới người dùng"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});
dulichamthuc.poi_submissions.createIndex({ review_status: 1 });
dulichamthuc.poi_submissions.createIndex({ submissed_by: 1 });
dulichamthuc.poi_submissions.createIndex({ slug: 1 }, { unique: true });

// Localization
dulichamthuc.createCollection("poi_localizations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "poi_id",
        "lang",
        "menu"
      ],
      properties: {
        poi_id:{
            bsonType: "objectId",
            description:"Khóa ngoại tới POI"
        },
        lang:{
            bsonType: "string",
            description: "mã ngôn ngữ"
        },
        menu:{
            bsonType: "string",
            description: "menu chuyển thành văn bản"
        },
        audio_url:{
            bsonType: ["string", "null"],
            description: "đường dẫn tts"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});
dulichamthuc.poi_localizations.createIndex(
  { poi_id: 1, lang: 1 },
  { unique: true }
);

// Audio task
dulichamthuc.createCollection("audio_tasks", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "localization_id",
        "status",
        "attempts",
        "heartbeat_at",
        "created_at",
        "expired_at"
      ],
      properties: {
        localization_id:{
            bsonType: "objectId",
            description: "khóa ngoại tới localizations"
        },
        status:{
            bsonType: "string",
            enum: [
                "PROGRESSING", 
                "FINISH", 
                "PAUSE", 
                "CANCELLED",
                "FAILED"
            ],
            description: "trạng thái họa động"
        },
        attempts:{
            bsonType: "int",
            description: "Số lần thử lại"
        },
        heartbeat_at:{
            bsonType: "date",
            description: "chạy lần cuối lúc"
        },
        created_at:{
            bsonType: "date",
            description: "tạo lúc"
        },
        expired_at:{
            bsonType: "date",
            description: "hết hạn lúc"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});
dulichamthuc.audio_tasks.createIndex({ status: 1, created_at: -1 });

// Admin user
dulichamthuc.createCollection("admin_users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "slug",
        "password_hash",
        "is_poi_owner_verified",
        "status",
        "name",
        "email_encrypted",
        "email_lookup_hash",
        "phone",
        "role_id"
      ],
      properties: {
        slug:{
            bsonType: "string",
            description: "đặt kiểu nguoi-01 hỗ trợ tìm kiếm và hiển thị url"
        },
        password_hash:{
            bsonType: "string",
            description: "mật khẩu băm"
        },
        is_poi_owner_verified:{
            bsonType: "bool",
            description: "đã xác minh chưa"            
        },
        status:{
            bsonType: "string",
            enum: [
                "ACTIVE", 
                "INACTIVE", 
                "SOFT_DELETE"
            ],
            description: ""            
        },
        name:{
            bsonType: "string",
            description: "tên"
        },
        email_encrypted:{
            bsonType: "string",
            description: "email phải được mã hóa"
        },
        email_lookup_hash:{
            bsonType: "string",
            description: "Chuỗi tìm kiếm"
        },
        phone:{
            bsonType: "string",
            description: "sđt phải được mã hóa"
        },
        role_id:{
            bsonType: "objectId",
            description: "khóa ngoại tới roles"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});
dulichamthuc.admin_users.createIndex({ email_lookup_hash: 1 }, { unique: true });
dulichamthuc.admin_users.createIndex({ slug: 1 }, { unique: true });

// Notification
dulichamthuc.createCollection("owner_notifications", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required:[
                "sender_id",
                "receiver_id",
                "submission_id",
                "is_read"
            ],
            properties: {
                sender_id:{
                    bsonType: "objectId",
                    description: "người gửi"
                },
                receiver_id:{
                    bsonType: "objectId",
                    description: "người nhận"
                },
                submission_id:{
                    bsonType: "objectId",
                    description: "về yêu cầu"
                },
                is_read:{
                    bsonType: "bool",
                    description: "đọc hay chưa"
                }
            }
        }
    },
    validationLevel: "strict",
    validationAction: "error"
});
dulichamthuc.owner_notifications.createIndex({ receiver_id: 1, is_read: 1 });

// Owner registration
dulichamthuc.createCollection("poi_owner_registrations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "slug",
        "status",
        "admin_note",
        "sender_id",
        "reviewer_id"
      ],
      properties: {
        slug:{
            bsonType: "string",
            description: ""
        },
        status:{
            bsonType: "string",
            enum: [
                "PENDING",
                "ACCEPTED",
                "REJECTED"
            ],
            description: "trạng thái xử lý"
        },
        admin_note:{
            bsonType: "string",
            description: "admin để lại lời nhắn"
        },
        sender_id:{
            bsonType: "objectId",
            description: "người dùng đăng kí"
        },
        reviewer_id:{
            bsonType: ["objectId", "null"],
            description: "admin duyệt"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});
dulichamthuc.poi_owner_registrations.createIndex({ sender_id: 1 });

// Role
dulichamthuc.createCollection("roles", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "slug",
        "name",
        "permissions",
        "priority"
      ],
      properties: {
        slug:{
            bsonType: "string",
            description: "đặt kiểu chu-cua-hang hỗ trợ tìm kiếm và hiển thị url"
        },
        name:{
            bsonType: "string",
            description: "tên role"
        },
        permissions:{
            bsonType: "array",
            description: "danh sách các permission",
            items: {
                bsonType: "string"
            }
        },
        priority:{
            bsonType: "int",
            description: "độ ưu tiên"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});
dulichamthuc.roles.createIndex({ slug: 1 }, { unique: true });
dulichamthuc.roles.createIndex({ priority: 1 });

// Audit log indexes
dulichamthuc.createCollection("audit_logs", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "action",
        "resource",
        "timestamp",
        "by_admin_id"
      ],
      properties: {
        action:{
            bsonType: "string",
            enum: [
                "ADD",
                "UPDATE",
                "DELETE",
                "ACCEPT",
                "REJECT"
            ],
            description: "hành động"
        },
        resource:{
            bsonType: "object",
            properties: {
                submission_id: {
                    bsonType: "objectId",
                    description: "yêu cầu đã duyệt, từ chối"
                },
                poi_owner_registration_id: {
                    bsonType: "objectId",
                    description: "đơn đăng kí đã duyệt, từ chối"
                },
                role:{
                    bsonType: "object",
                    properties: {
                        role_id:{
                            bsonType: "objectId",
                            description: "role bị ảnh hưởng"
                        },
                        changes: {
                            bsonType: "object",
                            properties: {
                                before: {
                                    bsonType: "object"
                                },
                                after: {
                                    bsonType: "object"
                                }
                            },
                            description: "lưu json object trước đó nếu cần"
                        }
                    }
                },
                poi: {
                    bsonType: "object",
                    properties: {
                        poi_id: {
                            bsonType: "objectId",
                            description: "poi bị ảnh hưởng"
                        },
                        changes: {
                            bsonType: "object",
                            properties: {
                                before: {
                                    bsonType: "object"
                                },
                                after: {
                                    bsonType: "object"
                                }
                            },
                            description: "lưu json object trước đó nếu cần"
                        }
                    }
                },
                user: {
                    bsonType: "object",
                    properties: {
                        user_id: {
                            bsonType: "objectId"
                        },
                        name: {
                            bsonType: "string"
                        },
                        changes: {
                            bsonType: "object",
                            properties: {
                                before: {
                                    bsonType: "object"
                                },
                                after: {
                                    bsonType: "object"
                                }
                            },
                            description: "lưu json object trước đó nếu cần"
                        }
                    }
                },

                // MENU ITEM
                menu: {
                    bsonType: "object",
                    properties: {
                        menu_item_id: {
                            bsonType: "objectId"
                        },
                        poi_id: {
                            bsonType: "objectId",
                            description: "POI chứa món ăn"
                        },
                        name: {
                            bsonType: "string"
                        },
                        changes: {
                            bsonType: "object",
                            properties: {
                                before: {
                                    bsonType: "object"
                                },
                                after: {
                                    bsonType: "object"
                                }
                            }
                        }
                    }
                }
            },
            description: "chi tiết hành động"
        },
        timestamp:{
            bsonType: "date",
            description: "thời điểm diễn ra"
        },
        by_admin_id:{
            bsonType: "objectId",
            description: "admin đã làm"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});
dulichamthuc.audit_logs.createIndex({ by_admin_id: 1, timestamp: -1 });
