from itertools import chain
import joblib

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    JSON,
    Table,
    ForeignKey,
    BigInteger,
    TIMESTAMP,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from lecrapaud.db.models.base import Base
from lecrapaud.db.models.utils import create_association_table

# jointures
lecrapaud_experiment_target_association = create_association_table(
    name="experiment_target_association",
    table1="experiments",
    column1="experiment",
    table2="targets",
    column2="target"
)


class Experiment(Base):

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    name = Column(String(50), nullable=False)
    path = Column(String(255))  # we do not have this at creation time
    type = Column(String(50), nullable=False)
    size = Column(Integer, nullable=False)
    train_size = Column(Integer)
    val_size = Column(Integer)
    test_size = Column(Integer)
    corr_threshold = Column(Float, nullable=False)
    max_features = Column(Integer, nullable=False)
    percentile = Column(Float, nullable=False)
    number_of_groups = Column(Integer)
    list_of_groups = Column(JSON)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    train_start_date = Column(DateTime)
    train_end_date = Column(DateTime)
    val_start_date = Column(DateTime)
    val_end_date = Column(DateTime)
    test_start_date = Column(DateTime)
    test_end_date = Column(DateTime)
    context = Column(JSON)

    feature_selections = relationship(
        "FeatureSelection",
        back_populates="experiment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    model_selections = relationship(
        "ModelSelection",
        back_populates="experiment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    targets = relationship(
        "Target",
        secondary=lecrapaud_experiment_target_association,
        back_populates="experiments",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "name",
            name="uq_experiments_composite",
        ),
    )

    def get_features(self, target_number: int):
        targets = [t for t in self.targets if t.name == f"TARGET_{target_number}"]
        if targets:
            target_id = targets[0].id
            feature_selection = [
                fs for fs in self.feature_selections if fs.target_id == target_id
            ]
            if feature_selection:
                feature_selection = feature_selection[0]
                features = [f.name for f in feature_selection.features]
                return features

        # fallback to path if no features found
        features = joblib.load(f"{self.path}/TARGET_{target_number}/features.pkl")
        return features

    def get_all_features(self, date_column: str = None, group_column: str = None):
        target_idx = [target.id for target in self.targets]
        _all_features = chain.from_iterable(
            [f.name for f in fs.features]
            for fs in self.feature_selections
            if fs.target_id in target_idx
        )
        _all_features = list(_all_features)

        # fallback to path if no features found
        if len(_all_features) == 0:
            _all_features = joblib.load(f"{self.path}/preprocessing/all_features.pkl")

        all_features = []
        if date_column:
            all_features.append(date_column)
        if group_column:
            all_features.append(group_column)
        all_features += _all_features
        all_features = list(dict.fromkeys(all_features))

        return all_features
