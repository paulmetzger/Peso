from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


class ThroughputSample(Base):
    __tablename__           = 'ThroughputSample'
    experiment_name         = Column(String(100), primary_key=True)
    input_size              = Column(Integer, primary_key=True)
    relative_deadline       = Column(Integer, primary_key=True)
    worker_wcet             = Column(Integer, primary_key=True)
    dop                     = Column(Integer, primary_key=True)
    with_batching           = Column(Integer, primary_key=True)
    sample                  = Column(Integer, primary_key=True)
    batch_size              = Column(Integer, primary_key=True)
    success                 = Column(Integer, nullable=False)
    min_interarrival_time   = Column(Integer, nullable=False)


class BatchSizeModelAccuracySample(Base):
    __tablename__           = 'BatchSizeModelAccuracySample'
    sample_application_name = Column(String(100), primary_key=True)
    input_size              = Column(Integer, primary_key=True)
    relative_deadline       = Column(Integer, primary_key=True)
    worker_wcet             = Column(Integer, primary_key=True)
    period                  = Column(Integer, primary_key=True)
    is_oracle               = Column(Integer, primary_key=True)
    sample                  = Column(Integer, primary_key=True)
    batch_size              = Column(Integer, nullable=False)
    success                 = Column(Integer, nullable=False)
    deadline_missed         = Column(Integer, nullable=False)


class DOPModelAccuracySample(Base):
    __tablename__           = 'DOPModelAccuracySample'
    sample_application_name = Column(String(100), primary_key=True)
    input_size              = Column(Integer, primary_key=True)
    relative_deadline       = Column(Integer, primary_key=True)
    worker_wcet             = Column(Integer, primary_key=True)
    period                  = Column(Integer, primary_key=True)
    is_oracle               = Column(Integer, primary_key=True)
    sample                  = Column(Integer, primary_key=True)
    batch_size              = Column(Integer, nullable=False)
    dop                     = Column(Integer, nullable=False)
    success                 = Column(Integer, nullable=False)
    matched_throughput      = Column(Integer, nullable=False)


class ThroughputHeatmapSample(Base):
    __tablename__           = 'ThroughputHeatmapSample'
    sample_application_name = Column(String(100), primary_key=True)
    input_size              = Column(Integer, primary_key=True)
    relative_deadline       = Column(Integer, primary_key=True)
    worker_wcet             = Column(Integer, primary_key=True)
    batch_size              = Column(Integer, primary_key=True)
    dop                     = Column(Integer, primary_key=True)
    sample                  = Column(Integer, primary_key=True)
    data_type               = Column(String(10), primary_key=True)
    min_period              = Column(Integer, nullable=False)
    compiled                = Column(Integer, nullable=False)
    missed_deadline         = Column(Integer, nullable=False)
    run_time_error          = Column(Integer, nullable=False)


class ThroughputWithHandImplementations(Base):
    __tablename__           = 'ThroughputWithHandImplementations'
    sample_application_name = Column(String(100), primary_key=True)
    input_size              = Column(Integer, primary_key=True)
    relative_deadline       = Column(Integer, primary_key=True)
    worker_wcet             = Column(Integer, primary_key=True)
    dop                     = Column(Integer, primary_key=True)
    is_hand_implementation  = Column(Integer, primary_key=True)
    sample_count            = Column(Integer, primary_key=True)
    batch_size              = Column(Integer, nullable=False)
    min_period              = Column(Integer, nullable=False)


'''The below experiment likely does not make sense'''
'''class ThroughputLossOverOptimumBatchSizeSample(Base):
        __tablename__           = 'ThroughputLossOverOptimumBatchSizeSample'
        experiment_name         = Column(String(100), primary_key=True)
        input_size              = Column(Integer, primary_key=True)
        relative_deadline       = Column(Integer, primary_key=True)
        worker_wcet             = Column(Integer, primary_key=True)
        dop                     = Column(Integer, primary_key=True)
        with_batching           = Column(Integer, primary_key=True)
        batch_size              = Column(Integer, primary_key=True)
        success                 = Column(Integer, nullable=False)
        min_interarrival_time   = Column(Integer, nullable=False)'''


engine = create_engine('sqlite:///rt.db')
Base.metadata.create_all(engine)