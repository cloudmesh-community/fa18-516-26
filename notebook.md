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
* Participating in Piazza discussion and answering other students' question
* Selecting the following sections for contribution:
	* Lambda Expressions
	* Generators 
	* Non Blocking Threads
	* Subprocess
	* Queue 
* Selecting the following chapter for contribution: 
	* Apache OpenWhisk
* Starting working on `Parallel Remote Jobs` assignment, part `c`, `c1` and `e`: 
> c) develop a task mechanism to manage and distribute the jobs on the machine using subprocess and a queue. Start with one job per machine,  
c.1) take c and do a new logic where each machine can take multiple jobs
e) develop a test program that distributes a job to the machines calculates the job and fetches the result back. This is closely related to c, but instead of integrating it in c the movement of the data to and from the job is part of a separate mechanism, It is essentially the status of the calculation. Once all results are in do the reduction into a single result. Remember you could do result calculations in parallel even if other results are not there i