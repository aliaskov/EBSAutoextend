import boto3
import time
import datetime
import os

# Manually configure EC2 region, account IDs, timezone
# ec = boto3.client('ec2', region_name=os.getenv('REGION'))
ec = boto3.client('ec2')


# os.environ['TZ'] = os.getenv('TZ')


# Nothing to configure below this line

def get_volume_size():
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

            # SSM actions
            if tag_key == 'AutoExtend' and volume['State'] == 'in-use' and volume['VolumeType'] != 'standard':
                print "Volume ID is " + vol_id
                ssm = boto3.client('ssm')
                ins_id = volume['Attachments'][0]['InstanceId']
                print "Instance ID is " + ins_id
                aws_attached = volume['Attachments'][0]['Device']
                vol_size = volume['Size']
                print "The volume " + vol_id + " is " + str(vol_size) + "Gb, " + volume[
                    'State'] + " and attached as " + aws_attached
                bash_command = " if [ -n \"$(lsblk " + aws_attached + " -n --output=MOUNTPOINT | tr -d \'\\n\\r\\t\')\" ]; then echo $(df --o=pcent " + aws_attached + "| tail -n +2 | cut -d '%' -f 1 ); fi "
                command = ssm.send_command(InstanceIds=[ins_id], DocumentName='AWS-RunShellScript',
                                           Comment='Checking used space', Parameters={"commands": [bash_command]})
                com_id = command['Command']['CommandId']
                print "SSM command ID is " + com_id
                print "bash command is " + bash_command

                # Timeout to get ssm response don't forget to add while loop
                time.sleep(1)
                response = ssm.list_command_invocations(CommandId=com_id, Details=True)
                used_space = response['CommandInvocations'][0]['CommandPlugins'][0]['Output']
                print used_space

                # Create tag on volume to have some info
                if used_space:
                    ec.create_tags(
                        Resources=[vol_id],
                        Tags=[
                            {'Key': '%Used space on ' + aws_attached,
                             'Value': used_space}
                        ]
                    )
                    if int(used_space) <= 70:
                        print "less than 70% used"
                    else:
                        print "more than 70% used, let's resize"
                        disk_resize(vol_id, vol_size)


def disk_resize(vol_id, vol_size):
    vol_extend_multiplier = 1.2
    vol_new_size = round(int(vol_size)) * vol_extend_multiplier
    ec.modify_volume(
        VolumeId=vol_id,
        Size=int(vol_new_size),
    )
    ec.create_tags(
        Resources=[vol_id],
        Tags=[
            {'Key': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
             'Value': "New volume size is  " + int(vol_new_size) + " Gb "}
        ]
    )

def lambda_handler(event, context):
    get_volume_size()
    return 'successful'


if __name__ == '__main__':
    lambda_handler([], [])
