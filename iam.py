#import os module to read files in system
import os 
#import re module to search specific pattern
import re 
#import git module to compare th files and commites and branches
import git 
#import boto3 to give api calls to AWS
import boto3

'''Regular expression to match AWS IAM keys as AWS access keys are always start with AKIA and other 16 characters with capital letters and number from 0-9'''
aws_key_pattern = re.compile(r'AKIA[0-9A-Z]{16}')
#returns all the AWS access keys
def search_for_iam_keys(content):
    return aws_key_pattern.findall(content)

def validate_iam_key(key):
    # Replace with your AWS IAM role ARN for key validation
    role_arn = 'arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_ROLE_NAME'
    
    # Initialize AWS session and STS client
    session = boto3.Session()
    sts_client = session.client('sts')

    try:
        sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='IAMKeyValidationSession'
        )
        return True
    except:
        return False
#to scan all the files in the repository
def scan_repository(repo_path):
    repo = git.Repo(repo_path)#intialise repo in the local directory
    for branch in repo.branches: #looping if more than one branch occurs 
        print(f"Scanning branch: {branch.name}")#printing the branch name which it is scanning
        for commit in repo.iter_commits(branch.name): #looping for all the commits in the branch
            parent_commit = commit.parents[0] if commit.parents else None # comparing the parent commit with the current commits
            if parent_commit:
                diff_index = parent_commit.diff(commit)
                for diff in diff_index:
                    file_path = os.path.join(repo_path, diff.a_path)
                    if os.path.exists(file_path):
                        with open(file_path, "r") as file: #opening the files in the directory
                            content = file.read()#reading the content in files
                            iam_keys = search_for_iam_keys(content)
                            for key in iam_keys:
                                if validate_iam_key(key):#validating them  by using boto3
                                    print(f"Valid IAM key found in {file_path}: {key}")
                                else:
                                    print(f"Invalid IAM key found in {file_path}: {key}")

if __name__ == "__main__":
    # Replace with the path to the local repository make sure you turn \ into \\
    repository_path = "<path>"
    scan_repository(repository_path)
