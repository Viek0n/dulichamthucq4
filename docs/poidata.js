
const poiDB = db.getSiblingDB("poi-service-db");

// Replace this with an existing admin user's _id from user-service-db.
const ownerId = ObjectId("68f000000000000000000001");

const pois = [
  {
    name: "Cơm Quê Hội An",
    address: "12 Đường Nguyễn Huệ, Hội An, Quảng Nam",
    open_at: "07:00",
    close_at: "21:00",
    contact: "0900000001",
    image: "https://example.com/images/com-que-hoi-an.jpg",
    latitude: 15.8801,
    longitude: 108.3380,
    trigger_radius: 30.0,
    is_delete: false,
    poi_owner_id: ownerId
  },
  {
    name: "Phở Bò Hà Nội",
    address: "25 Đường Lê Lợi, Hà Nội",
    open_at: "06:00",
    close_at: "22:00",
    contact: "0900000002",
    image: "https://example.com/images/pho-bo-ha-noi.jpg",
    latitude: 21.0285,
    longitude: 105.8542,
    trigger_radius: 30.0,
    is_delete: false,
    poi_owner_id: ownerId
  },
  {
    name: "Bánh Mì Sài Gòn",
    address: "18 Đường Nguyễn Trãi, TP. Hồ Chí Minh",
    open_at: "06:00",
    close_at: "20:00",
    contact: "0900000003",
    image: "https://example.com/images/banh-mi-sai-gon.jpg",
    latitude: 10.7626,
    longitude: 106.6820,
    trigger_radius: 30.0,
    is_delete: false,
    poi_owner_id: ownerId
  },
  {
    name: "Bún Bò Cố Đô",
    address: "36 Đường Trần Hưng Đạo, Huế",
    open_at: "06:30",
    close_at: "21:00",
    contact: "0900000004",
    image: "https://example.com/images/bun-bo-co-do.jpg",
    latitude: 16.4637,
    longitude: 107.5909,
    trigger_radius: 30.0,
    is_delete: false,
    poi_owner_id: ownerId
  },
  {
    name: "Hải Sản Đà Nẵng",
    address: "42 Đường Võ Nguyên Giáp, Đà Nẵng",
    open_at: "10:00",
    close_at: "23:00",
    contact: "0900000005",
    image: "https://example.com/images/hai-san-da-nang.jpg",
    latitude: 16.0544,
    longitude: 108.2470,
    trigger_radius: 30.0,
    is_delete: false,
    poi_owner_id: ownerId
  }
];

const menuItems = [
  // POI 1: Cơm Quê Hội An
  {
    poi_id: pois[0]._id,
    name: "Cơm gà Hội An",
    price: 50000
  },
  {
    poi_id: pois[0]._id,
    name: "Cao lầu",
    price: 45000
  },
  {
    poi_id: pois[0]._id,
    name: "Bánh bao bánh vạc",
    price: 40000
  },

  // POI 2: Phở Bò Hà Nội
  {
    poi_id: pois[1]._id,
    name: "Phở bò tái",
    price: 45000
  },
  {
    poi_id: pois[1]._id,
    name: "Phở bò chín",
    price: 45000
  },
  {
    poi_id: pois[1]._id,
    name: "Phở bò đặc biệt",
    price: 65000
  },

  // POI 3: Bánh Mì Sài Gòn
  {
    poi_id: pois[2]._id,
    name: "Bánh mì thịt nguội",
    price: 25000
  },
  {
    poi_id: pois[2]._id,
    name: "Bánh mì xíu mại",
    price: 30000
  },
  {
    poi_id: pois[2]._id,
    name: "Bánh mì gà nướng",
    price: 35000
  },

  // POI 4: Bún Bò Cố Đô
  {
    poi_id: pois[3]._id,
    name: "Bún bò Huế thường",
    price: 40000
  },
  {
    poi_id: pois[3]._id,
    name: "Bún bò giò heo",
    price: 50000
  },
  {
    poi_id: pois[3]._id,
    name: "Bún bò đặc biệt",
    price: 60000
  },

  // POI 5: Hải Sản Đà Nẵng
  {
    poi_id: pois[4]._id,
    name: "Mực nướng",
    price: 120000
  },
  {
    poi_id: pois[4]._id,
    name: "Tôm hấp",
    price: 150000
  },
  {
    poi_id: pois[4]._id,
    name: "Nghêu hấp sả",
    price: 80000
  }
];

// Insert POIs first so their IDs exist before inserting menu items.
poiDB.POI.insertMany(pois);
poiDB.menu_items.insertMany(menuItems);

print("Inserted 5 POIs and 15 menu items.");
