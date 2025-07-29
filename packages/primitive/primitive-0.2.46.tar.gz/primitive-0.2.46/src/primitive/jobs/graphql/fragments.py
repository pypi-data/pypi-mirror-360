job_fragment = """
fragment JobFragment on Job {
    id
    pk
    slug
    name
    createdAt
    updatedAt
}
"""

job_run_fragment = """
fragment JobRunFragment on JobRun {
  id
  pk
  jobRunNumber
  createdAt
  updatedAt
  completedAt
  startedAt
  status
  conclusion
  job {
    id
    pk
    slug
    name
    createdAt
    updatedAt
  }
  jobSettings {
    containerArgs
    rootDirectory
    parseLogs
    parseStderr
    failureLevel
    repositoryFilename
    config
  }
  gitCommit {
    sha
    branch
    repoFullName
  }
}
"""

job_run_status_fragment = """
fragment JobRunStatusFragment on JobRun {
    id
    status
    conclusion
    parentPid
}
"""
