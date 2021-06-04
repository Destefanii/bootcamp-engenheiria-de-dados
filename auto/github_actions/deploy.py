import boto3
import logging
import os

logging.getLogger().setLevel(logging.INFO)
cloudformation_client = boto3.client('cloudformation')

def create_stack(stack_name, template_body, **kwargs):
    cloudformation_client.create_stack(
        StackName=stack_name,
        TemplateBody = template_body,
        Capabilities=['CAPABILITY_IAM','CAPABILITY_NAMED_IAM'],
        TimeoutInMinutes=5,
        OnFailure='ROLLBACK'
    )

    cloudformation_client.get_waiter('stack_create_complete').wait(
        StackName=stack_name,
        WaiterConfig={'Delay': 5, 'MaxAttempts': 600}
    )

    cloudformation_client.get_waiter('stack_exists').wait(StackName=stack_name)
    logging.info(f'CREATE COMPLETE')


def get_existing_stacks():
    response = cloudformation_client.list_stacks(
        StackStatusFilter=['REVIEW_IN_PROGRESS', 
                            'CREATE_FAILED', 
                            'UPDATE_ROLLBACK_FAILED', 
                            'UPDATE_ROLLBACK_IN_PROGRESS', 
                            'CREATE_IN_PROGRESS', 
                            'IMPORT_ROLLBACK_IN_PROGRESS', 
                            'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 
                            'ROLLBACK_IN_PROGRESS', 
                            'IMPORT_IN_PROGRESS', 
                            'DELETE_COMPLETE', 
                            'UPDATE_COMPLETE', 
                            'UPDATE_IN_PROGRESS', 
                            'DELETE_FAILED', 
                            'IMPORT_COMPLETE', 
                            'DELETE_IN_PROGRESS', 
                            'ROLLBACK_FAILED', 
                            'IMPORT_ROLLBACK_COMPLETE', 
                            'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS', 
                            'CREATE_COMPLETE', 
                            'IMPORT_ROLLBACK_FAILED', 
                            'UPDATE_ROLLBACK_COMPLETE',
                            'ROLLBACK_COMPLETE']
    )

    return [stack['StackName'] for stack in response ['StackSummaries']]

def _get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def create_or_update_stack():
    stack_name= 's3-bucket-ci-la-la'
    with open(_get_abs_path('bucket.yml')) as f:
        template_body = f.read()

    existing_stacks = get_existing_stacks()

    logging.info(f'CREATING STACK {stack_name}')
    create_stack(stack_name, template_body)

if __name__ == '__main__':
    create_or_update_stack()