from sqlalchemy import Column, Integer, String, Float, Enum 
from app.db.database import Base
import enum
class CategoryEnum(str, enum.Enum):
    INFORMATIQUE = "INFORMATIQUE"
    BUREAUTIQUE = "BUREAUTIQUE"
    MOBILIER = "MOBILIER"
    ELECTRICITE = "ELECTRICITE"
    CONSOMMABLE = "CONSOMMABLE"
    AUTRE = "AUTRE"

class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    prix = Column(Float, nullable=False)
    quantite = Column(Integer, default=0)
    categorie = Column(Enum(CategoryEnum), nullable=False, default=CategoryEnum.AUTRE)
