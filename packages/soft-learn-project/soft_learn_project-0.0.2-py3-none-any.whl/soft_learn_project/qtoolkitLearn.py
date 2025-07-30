import qtoolkit
import qtoolkit.core.data_objects


class QtoolkitLearn():
  def __init__(self):
    """https://matgenix.github.io/qtoolkit/user/install.html
    """
    pass

  def install(self):
    string = """pip install qtoolkit
    conda install qtoolkit
    """
    print(string)
    return None

  def get_resources(self,
                    queue_name='hfacnormal01',
                    job_name='vasp',
                    nodes=1,
                    process_placement=32,
                    processes_per_node=128,
                    time_limit=30000,
                    output_filepath='pbs.log',
                    error_filepath='pbs.err',):
    resources = qtoolkit.core.data_objects.QResources(queue_name=queue_name,
                                                      job_name=job_name,
                                                      nodes=nodes,
                                                      process_placement=process_placement,
                                                      #  processes=32,
                                                      processes_per_node=processes_per_node,
                                                      time_limit=time_limit,
                                                      output_filepath=output_filepath,
                                                      error_filepath=error_filepath,
                                                      )
    return resources
