from lib.report_base.assets_base.assets_base import AssetsBase


class Chambers(AssetsBase):
    class Chamber(object):
        def __init__(self, params):
            self.id = params[0]
            self.x = params[1]
            self.y = params[2]
            self.z = params[3]
            self.chamber_size = params[4]
            self.material = params[5]
            self.construction_year = params[6]
            self.status = params[7]
            self.observation = params[8]
            self.for_breakpressure = params[9]
            self.has_clorination = params[10]
            self.sector = params[11]
            self.cell = params[12]
            self.village = params[13]

    def __init__(self, wss_id):
        super().__init__(wss_id, "Chambers")
        self.chamber_type = ''

    def get_assets_info(self, db):
        query = "   SELECT "
        query += "     a.chamber_id, "
        query += "     round(cast(st_x(a.geom) as numeric),6) as x, "
        query += "     round(cast(st_y(a.geom) as numeric),6) as y,  "
        query += "     cast(ST_Value(e.rast, 1, a.geom) as integer) as z,  "
        query += "     a.chamber_size,  "
        query += "     a.material,  "
        query += "    COALESCE(a.rehabilitation_year, a.construction_year) as construction_year,  "
        query += "     b.status,  "
        query += "     a.observation,  "
        query += "     CASE WHEN a.is_breakpressure = true THEN 'YES' ELSE 'NO' END as for_breakpressure,  "
        query += "     CASE WHEN a.chlorination_unit = true THEN 'YES' ELSE 'NO' END as has_clorination, "
        query += "     h.sector, "
        query += "     g.cell, "
        query += "     f.village "
        query += "   FROM chamber a "
        query += "   INNER JOIN status b "
        query += "   ON a.status = b.code "
        query += "   INNER JOIN rwanda_dem_10m e "
        query += "   ON ST_Intersects(e.rast, a.geom) "
        query += "  INNER JOIN village f ON ST_Intersects(f.geom, a.geom) "
        query += "  INNER JOIN cell g ON f.cell_id = g.cell_id "
        query += "  INNER JOIN sector h ON f.sect_id = h.sect_id "
        query += "   WHERE a.chamber_type = '{0}' ".format(self.chamber_type)
        query += "   AND a.wss_id = {0}".format(self.wss_id)
        result = db.execute(query)
        self.assetsList = []
        for data in result:
            self.assetsList.append(Chambers.Chamber(data))
        return self.assetsList

    def add_title(self, doc):
        doc.add_heading('List of {0}'.format(self.chamber_type), level=4)

    def create_column_list(self):
        return [#AssetsBase.Column('ID', 'id', ''),
                AssetsBase.Column('X', 'x', ''),
                AssetsBase.Column('Y', 'y', ''),
                AssetsBase.Column('Z', 'z', ''),
                AssetsBase.Column('Sector', 'sector', ''),
                AssetsBase.Column('Cell', 'cell', ''),
                AssetsBase.Column('Village', 'village', ''),
                AssetsBase.Column('Construction', 'construction_year', ''),
                AssetsBase.Column('Status', 'status', ''),
                AssetsBase.Column('Size', 'chamber_size', ''),
                AssetsBase.Column('Material', 'material', ''),
                AssetsBase.Column('Break pressure', 'for_breakpressure', 'NO'),
                AssetsBase.Column('Chlorination Unit', 'has_clorination', 'NO'),
                AssetsBase.Column('Observation', 'observation', '')]

    def create(self, db, doc):
        chamber_type_list = ["Valve chamber", "Air release chamber", "Washout chamber",
                             "Break Pressure chamber", "PRV chamber",
                             "Starting chamber", "Collection chamber"]
        for chamber_type in chamber_type_list:
            self.chamber_type = chamber_type
            if chamber_type_list.index(chamber_type) == 0:
                self.add_main_title(doc)
            self.get_assets_info(db)
            if len(self.assetsList) > 0:
                self.add_title(doc)
                self.add_table(doc)
                self.add_break(doc)
