## E616 - Vafa Andalibi 

# Summary of *batch* (Slurm) command

The *batch* command is a tool that can be used to submit jobs to a remote cluster which is (already) using Slurm workload manager. This command works as a front end to make job submission, result retrial and remote cleaning more convenient. The full documentation for the batch command as well as corresponding examples is [available online](https://cloudmesh-community.github.io/cm/batch.html) but for some reason it is not indexed in the table of content of [cm4 documentation](https://cloudmesh-community.github.io/cm/index.html). In the following sections, the main assumptions are presented and possible improvement of the tool are described in form of questions: 

* Each job created by this tool only takes in one remote Slurm cluster. So in case the user wants to submit a job to more than one Slurm cluster, she has to create another job manually. Is it useful to submit one job to more than one Slurm cluster? 

* The batch command assumes that the Slurm file is already created and debugged. Is it useful for the batch command to build the Slurm file? 

* The batch tool uses the SSH config file for initiating the connection and authentication (either credentials or private key). 

* The input type of the Slurm job is assumed to be either a set of command line arguments possibly accompanied by other data files. 

* Similar to vcluster command, the Slurm command also saves its temporary configurations, including current submitted jobs and required information to check/retrieve the results, in a yaml file located in the *workspace* folder. Should this be changed to use MongoDB instead of a local file? 
  *itemize*

