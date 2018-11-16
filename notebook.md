This is the progress report for E516-Engineering cloud computing course.

# Week Fri 08/31/18 - Thu 09/06/18
* Taking the plagiarism test
* Cloning and initializing the repository.
* Getting myself familiar with the `cloudmesh-community` organization, specifically the `book` repository.
* Reading course-related material in `book/chapters/class/`.
* Preparing the local infrastructure for the course.
* Participating in Piazza discussions and answering questions
* Starting reading chapter 8: Data Center

# Week Fri 09/7/18 - Thu 09/13/18

* Fixed the typos in the whole repository including 750+ typos on 150+ files. Note that doing this in a way not to damage the repository takes more time than expected.
* Contributed the following sections:
	* Lambda Expressions
	* Iterators
* Participating in Piazza discussion and answering other students' question
* Starting working on `Parallel Remote Jobs` assignment, part `c`, `c1` and `e`:
> c) develop a task mechanism to manage and distribute the jobs on the machine using subprocess and a queue. Start with one job per machine,
c.1) take c and do a new logic where each machine can take multiple jobs
e) develop a test program that distributes a job to the machines calculates the job and fetches the result back.

# Week Fri 09/14/18 - Thu 09/20/18

* Contributing a chapter namely `Parallel Computing In Pythong` containing sections for:
	* Thread vs Threading
	* Locks in Threading
  * Process
  * Pool
  * Locks in multiprocessing
  * Process communication

# Week Fri 09/21/18 - Thu 09/27/18

* Updating `README.yml` file and adding the contributions to it.
* First commit of Apache OpenWhisk chapter.
* OpenWhisk synopsis and workflow subsections added.

# Week Fri 09/28/18 - Thu 10/04/18

Note: I had two midterms this week
* Answering some question of students in Piazza
* Fixing the `epub` symbol issue in Linux and posting it in `FAQs` in Piazza

# Week Fri 10/05/18 - Thu 10/11/18

I was concentrating on reading the book. On the technical side, I was working on:

* Virtualization, specifically QEMU/KVM and docker.
* Amazon AWS services (free account)
* Microsoft Azure services (free account)

# Week Fri 10/12/18 - Thu 10/18/18

* Completing the OpenWhisk workflow and submitting pull request.
* Completing the installation process of the OpenWhisk locally
* Starting the hello world example of OpenWhisk for running locally

# Week Fri 10/19/18 - Thu 10/25/18

* OpenWhisk chapter containing OpenWhisk workflow, local setup tutorial, hello-world example and custom action example completed, pull request made and merged
* First version of Parallel Remote Jobs tool was developed and tested and future steps of the project was discussed with the professor. 

# Week Fri 10/26/18 - Thu 11/1/18

- Parallel remote jobs code went through a lot of changes and is now integrated into the cm4 command as virtual cluster (`vcluster`) with the following usages: 

  ```bash
  cm4 vcluster create virtual-cluster VIRTUALCLUSTER_NAME --clusters=CLUSTERS_LIST [--computers=COMPUTERS_LIST] [--debug]
  cm4 vcluster destroy virtual-cluster VIRTUALCLUSTER_NAME
  cm4 vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params out:stdout [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-now [default=True]]  [--debug]
  cm4 vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params out:file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-now [default=True]]  [--debug]
  cm4 vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:stdout [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]]  [--download-now [default=True]]  [--debug]
  cm4 vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-now [default=True]]  [--debug]
  cm4 vcluster create runtime-config CONFIG_NAME PROCESS_NUM in:params+file out:stdout+file [--fetch-proc-num=FETCH_PROCESS_NUM [default=1]] [--download-now [default=True]]  [--debug]
  cm4 vcluster set-param runtime-config CONFIG_NAME PARAMETER VALUE
  cm4 vcluster destroy runtime-config CONFIG_NAME
  cm4 vcluster list virtual-clusters [DEPTH [default:1]]
  cm4 vcluster list runtime-configs [DEPTH [default:1]]
  cm4 vcluster run-script --script-path=SCRIPT_PATH --job-name=JOB_NAME --vcluster-name=VIRTUALCLUSTER_NAME --config-name=CONFIG_NAME --arguments=SET_OF_PARAMS --remote-path=REMOTE_PATH> --local-path=LOCAL_PATH [--argfile-path=ARGUMENT_FILE_PATH] [--outfile-name=OUTPUT_FILE_NAME] [--suffix=SUFFIX] [--overwrite]
  cm4 vcluster fetch JOB_NAME
  cm4 vcluster clean-remote JOB_NAME PROCESS_NUM
  cm4 vcluster test-connection VIRTUALCLUSTER_NAME PROCESS_NUM
  ```

* `README` of virtual cluster tool is updated and examples of `cm4 vcluster` added. 

# Week Fri 11/2/18 - Thu 11/8/18

I had a midterm this week + 2 assignment, therefore could not work on the project very much 

# Week Fri 11/9/18 - Thu 11/15/18

* Starting the `cm4 batch` as a subcommand for slurm suport

