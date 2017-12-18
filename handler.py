
import boto3
import datetime
import time
import os

# Manually configure EC2 region, account IDs, timezone
ec = boto3.client('ec2', region_name=os.getenv('REGION'))
os.environ['TZ'] = os.getenv('TZ')


# Nothing to configure below this line

def extend_volume_size():
    # Find volumes tagged with tag "AutoExtend"
    volumes = ec.describe_volumes(
        Filters=[
            {'Name': 'tag-key', 'Values': ['AutoExtend']},
        ]
    ).get(
       'Volumes', []
    )

    print 'Number of volumes with AutoExtend tag: %d' % len(volumes)

    for volume in volumes:
        vol_id = volume['VolumeId']

        # Loop over all tags and grab out relevant keys
        for name in volume['Tags']:
            tag_key = name['Key']
            tag_val = name['Value']
            # print '...Found EBS volume key %s : %s ' % ( tag_key, tag_val );

        # SSM actions
            if tag_key == 'AutoExtend':
        #Need to get instance ID!
        
                ssm = boto3.client('ssm')    
                testCommand = ssm.send_command( InstanceIds=[ 'i-123123123123' ], DocumentName='AWS-RunShellScript', Comment='la la la', Parameters={ "commands":[ "ip config" ]  } )
                print 'ssm output'
                
        # Create time tag on volume to have some history
                ec.create_tags(
                  Resources=[vol_id],
                  Tags=[
                    {'Key': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Value': 'Volume was extended' }
                  ]
                )

def lambda_handler(event, context):
    extend_volume_size()
    return 'successful'

