import sys

from resume_checker.resume_checker import create_report_of

if __name__ == "__main__":
    create_report_of(sys.argv[1])
