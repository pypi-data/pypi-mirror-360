from django.core.management.base import BaseCommand, CommandError

from nkunyim_iam.management.commands.commands import (
    DataxNewCommand, 
    DataxRevCommand, 
    DataxRunCommand
)



class Command(BaseCommand):
    help = 'Send email reminders to inactive users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--new',
            type=str,
            help='Generate a new DataxMigration file with the given name.'
        )

        parser.add_argument(
            '--run',
            type=str,
            help='Run a DataxMigration from a give file name.'
        )

        parser.add_argument(
            '--rev',
            type=str,
            help='Reverse a DataxMigration from a given file name.'
        )
        
    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("Datax Migration ") + self.style.SQL_KEYWORD("Started!"))
        
        if options['new']:
            info = "Generating a new Datax Migration file: "
            msg = "A new Datax Migration file has been generated successfully at: "
            cmd = DataxNewCommand(input_name=options['new'])
        elif options['run']:
            info = "Running Datax Migration from the file: "
            msg = "Datax Migration has been migrated from the file: "
            cmd = DataxRunCommand(input_name=options['run'])
        elif options['rev']:
            info = "Reversing Datax Migration from the file: "
            msg = "Datax Migration has been reversed from the file: "
            cmd = DataxRevCommand(input_name=options['rev'])
        else:
            raise CommandError('The --some-required-option is missing.')
            
            
        self.stdout.write(self.style.HTTP_SUCCESS(info) + self.style.HTTP_INFO(cmd.python_file_name))
        
        res = cmd.go()
        if res: 
            self.stdout.write(self.style.HTTP_SUCCESS(res))
            self.stdout.write(self.style.HTTP_INFO("Datax Migration ") + self.style.ERROR_OUTPUT("Failed!"))
        else:
            self.stdout.write(self.style.HTTP_SUCCESS(msg) + self.style.HTTP_INFO(cmd.pyhton_file_path))
            self.stdout.write(self.style.HTTP_INFO("Datax Migration ") + self.style.SUCCESS("Successful!"))
