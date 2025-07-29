import datetime

TIME_FORMAT = "%Y%m%d_%H%M%S"


def get_base_name(name):
    return f"{name}_{datetime.datetime.now().strftime(TIME_FORMAT)}.json"


def run_pipeline(pipeline_name, ingestion: object, outputs: list = None, name_template=get_base_name):
    """
    Function to run a pipeline with the given name, ingestion method, and outputs.

    :param name: Name of the pipeline.
    :param ingestion: Ingestion method to fetch data.
    :param outputs: List of output methods to process the data.
    :return: None
    """

    if outputs is None:
        outputs = []
    data = ingestion.get()
    print("Data fetched from ingestion:", data)

    for output in outputs:
        print(f"Processing output with {output.__class__.__name__}")
        output.write(data, name_template(pipeline_name))
