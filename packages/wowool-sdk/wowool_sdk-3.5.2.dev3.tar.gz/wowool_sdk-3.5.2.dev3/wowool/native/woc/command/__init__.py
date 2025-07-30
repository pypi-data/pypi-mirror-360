import wowool.native.woc.command.compile as compile
import wowool.native.woc.command.project as project
import wowool.native.woc.command.create as create
import wowool.native.woc.command.version as version


class CommandFactory:
    def __call__(self, **kwargs):
        if "version" in kwargs and kwargs["version"] is True:
            return version.command
        elif kwargs["create"]:
            return create.command
        elif kwargs["project"]:
            return project.command
        else:
            return compile.command
