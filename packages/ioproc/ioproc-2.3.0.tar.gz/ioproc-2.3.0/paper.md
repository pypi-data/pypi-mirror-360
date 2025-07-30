---
title: 'ioProc: A light-weight workflow manager in Python'
tags:
  - Python
  - workflow management
  - data science
  - data pipeline
  
authors:
  - name: Benjamin Fuchs
    orcid: 0000-0002-7820-851X
    affiliation: 1
  - name: Judith Vesper
    orcid: 0000-0002-1783-0196
    affiliation: 1
  - name: Felix Nitsch
    orcid: 0000-0002-9824-3371
    affiliation: 1
  - name: Niklas Wulff
    orcid: 0000-0002-4659-6984
    affiliation: 1
	
affiliations:
 - name: German Aerospace Center (DLR), Institute of Engineering Thermodynamics, Department of Energy Systems Analysis, Pfaffenwaldring 38-40, 70569 Stuttgart, Germany
   index: 1
date: 01 June 2020
---


# Summary
ioProc (&quot;input/output processing&quot;) is a low level workflow manager in Python providing robust, scalable and reproducible data pipelines. It is developed for and in the scientific context of energy systems analysis but widely applicable in other scientific fields. ioProc was designed with a specific user group in mind: scientists without a thorough programming education or on the beginner level. Scientists&#39; usual prime interest lies in low-maintenance tools, yet providing adaptability solving their problems. Also, most of this user group is accustomed to script based or single file monolythic analysis pipelines and in recent years more frequently to Jupyter notebooks (Kluyver, Ragan-Kelley et al. 2016). For small to medium departments of scientist, forming a group with a shared software base, it is increasingly complicated to maintain standards for sharing code reliably across users, projects and topics. Jupyter notebooks and the provided server infrastructure provide one very specific solution for these challenges which might not fit every scientific research groups&#39; needs, especially when it comes to migrating to a deployable application. ioProc tries to solve this issue in its own unique way, by providing a basic, easy to apply framework which enforces structuring and provides the basis for code sharing. In combination with a concurrent versions system (cvs), ioProc can easily be used to create shared, versioned code bases over scientists, projects and topics, facilitating the exchange of code in a dynamic scientific research environment.

There is already a large number of workflow frameworks that have also been developed for data science purposes, such as Airflow [1], Kedro [2], Luigi [3], Pinball [4] and Snakemake [5]. Most of these frameworks, however, are more complex and require a deeper understanding of their software architecture. While this might be easy and even familiar to regular software engineers or programming inclined scientists, the average scientist might perceive these frameworks as distracting or unnecessary overhead. Especially when it comes to debugging or advanced features like parallel processing, complex frameworks create additional maintenance and learning overhead, which not everybody is inclined to. Deploying or publishing analysis software or data-flow pipelines in a scientific context, the dependency of a complicated workflow tool can be a hindrance, especially when it introduces specific hardware and software dependencies.

ioProc tries to negotiate a reasonable compromise between the underlying varying requirements. It is developed for scientists (i) wanting an easy to understand and easy to use workflow manager, (ii) looking for a framework that gets into their way as little as possible, while (iii) keeping the possibility to share or publish a code base within their workgroup, department or the public. By its structure and approach, ioProc encourages its users to adhere to well established software engineering principles like the single responsibility principle or DRY (don&#39;t repeat yourself). It thus supports and benefits the maintenance of software created on top of it.

## Features
- Written in pure Python
- Open source (MIT license)
- Pip installable
- Support of shared code bases by cvs of the users choice
- Clean, extensible, human readable configuration
- Separation of data, configuration and code in project specific workflows
- Data tracing and logging throughout operations
- Checkpoints to suspend and resume workflows

# Architecture
ioProc was designed based on the &quot;pipes and filters&quot; architectural pattern. Its central design principles are single responsibility, DRY and YAGNI. The design approach favors composition and aims towards thorough encapsulation. Its fundamental concepts are:

- Actions (individual operations that can be chained into a workflow)
- Managers (dict-like Python objects responsible for holding data and tracking accesses and modifications)
- Multiple code bases (folders containing Python modules with action definitions)
- Auto discovery (actions from code bases auto register with the framework)

The number of concepts is kept as small as possible in order to limit the amount of concepts to be grasped by an end user to a minimum. An understanding of the auto discovery approach for actions is for example not necessary for applying ioProc to use cases.

## Components
### Actions
Actions are the basic building blocks of ioProc workflows. A family of actions comprises a code base. At their heart, actions are Python functions with an enforced interface. They are automatically chained together into a user defined workflow and can be grouped into namespaces. An easy to learn syntax, based on Python decorators is used to mark actions for auto discovery. This enables the user to define additional support functions in the same file alongside actions without them being treated as actions. Finally, actions are able to call other actions inside of them. This composition approach provides the option to reduce code duplication to a minimum for extensions to existing actions.

### Configuration manager
The configuration manager is a dict-like object that parses the central configuration file and its extensions into one hierarchical dict-like config structure. The configuration manager provides access to the individual configuration of the current action (including parameters and static data) as well as the complete workflow configuration provided by the user.

### Data manager
The data manager is a dict-like object that stores and keeps track of all data sets used during a workflow. Each action is able to access the data manager, thus it is the overarching interface between actions. The data manager can create a log of all data sets stored and accessed during workflows for scientific documentation and reproducibility. ioProc currently does not enforce a specific data transport data type but it was designed with pandas DataFrames and Series in mind. Hence these data types are recommended for data handling.

### Action manager
This manager is used by the ioProc driver to access all known actions and is responsible for auto discovery of actions in known locations. The action manager is not accessed directly by users or actions. It is a dict-like object that is automatically created by the driver and populated at the beginning of a workflow sequence.

### Driver
The ioProc driver is responsible for instantiating the configuration manager, data manager, action manager, triggering the action auto discovery by the action manager and for executing the actions of the user supplied workflow.

### Command line interface
ioProc provides a command line interface that supports users in creating the default folder structure for ioProc workspaces, creating new projects and starting workflows. It is automatically installed by the pip installer and provides the user with a convenient way to start a new workflow/project.

## ioProc workspace
The ioProc default workspace separates code base from project space. It also supports multiple project spaces and code bases. By the standard ioProc configuration, the user can specify paths to folders containing ioProc actions. These are then automatically discovered and parsed during the workflow initialization. Although ioProc encourages aggregation of all actions inside the ioProc workspace, it does not enforce it at runtime, providing the users the option to come up with their own structure. The same holds true for projects. We strongly recommend, however, sticking to the default ioProc workspace structure to reduce complexity.

### Project space
In the project space, each project has its own subfolder. A project compromises of at least a configuration file (user.yaml), a driver file (run.py) and several log files after workflow execution (The runlog and the data log if requested. The data log documents data access and creation during the workflow). ioProc encourages users to place all data inside of the project space but does not enforce it, since data sources can be very diverse ranging from databases to simple csv files.

### Code base
The code base is a folder, containing Python files, which contain valid ioProc action definitions. The code base is defined in the central ioProc configuration file of an ioProc project, and can be switched between projects. ioProc checks for duplicates of actions based on their names and informs the user about them. Finally, by placing the code base into a cvs (like GIT) users can share their actions independent from their projects.

## Architecture component graph
The following graph shows the architectural layers and major components of ioProc:

![Figure 1: Architectural layers and major components of ioProc](fig1_componentview.png)

## Runtime graph
The following Figure shows the typical execution flow within ioProc.

![Figure 2: Schematic action workflow in ioProc](fig2_actionflow.png)

## Documentation:
ioProc is documented on ReadTheDocs. Furthermore cheat sheets are provided for installing ioProc, the ioProc workspace structure, setting up projects, creating actions and writing workflows.

A list of default actions are shipped with ioProc. The default actions are primarily for illustration purpose and serve the user as a starting point for writing its own actions.

The default actions shipped with ioProc are

- readExcel()
- checkpoint()
- printData()

which are explained in detail in the README.md file.

## Acknowledgements
We acknowledge support and contributions from Hedda Gardian, Kai von Krbek, Gabriel Pivaro and Kristina Nienhaus.


## References
[1](#sdfootnote1anc) https://github.com/apache/airflow

[2](#sdfootnote2anc) https://github.com/quantumblacklabs/kedro

[3](#sdfootnote3anc) https://github.com/spotify/luigi

[4](#sdfootnote4anc) https://github.com/pinterest/pinball

[5](#sdfootnote5anc) https://github.com/snakemake/snakemake
