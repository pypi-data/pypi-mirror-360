from flask_bauto import AutoBlueprint, dataclass, relationship
import bull_stack as bs

class Test(AutoBlueprint):
    @dataclass
    class Genus:
        name: str
        family: str
        species: list[int] = None
        #species: list[int] = relationship('Species', back_populates='genus', cascade="all, delete-orphan")

        def __str__(self):
            return self.name

        @property
        def actions(self):
            return [
                (f"/user/admin/profile/{self.id}", 'bi bi-app'),
                (f"/user/remove/{self.id}", 'bi bi-x-circle')
            ]
        
    @dataclass 
    class Species:
        genus_id: int
        name: str
        
    def show_species(self) -> str:
        return f"{self.query.genus.get(1).species_list}"

appstack = bs.BullStack(
    __name__, [Test(enable_crud=True,url_prefix=False)],
    sql_db_uri='sqlite:///project.db',
    admin_init_password='badmin', db_migration=True
)

def create_app():
    return appstack.create_app()
