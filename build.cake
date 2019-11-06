#addin nuget:?package=Cake.Docker&version=0.10.1
#addin nuget:?package=Cake.GitVersioning&version=3.0.26

using Nerdbank.GitVersioning;
//////////////////////////////////////////////////////////////////////
// ARGUMENTS
//////////////////////////////////////////////////////////////////////

var target = Argument("target", "Default");

//////////////////////////////////////////////////////////////////////
// PREPARATION
//////////////////////////////////////////////////////////////////////

VersionOracle versionOracle;

//////////////////////////////////////////////////////////////////////
// TASKS
//////////////////////////////////////////////////////////////////////

Task("Get-Version")
    .Does(() =>
{
    versionOracle = GitVersioningGetVersion();

    StartProcess("appveyor", new ProcessSettings {
        Arguments = new ProcessArgumentBuilder()
            .Append("UpdateBuild")
            .Append("-Version")
            .Append(versionOracle.SemVer2)
        }
    );
});

Task("Build-Docker-Container")
    .IsDependentOn("Get-Version")
    .Does(() =>
{
    var settings = new DockerImageBuildSettings
    {
        Tag = new string[]
        {
            $"clcrutch/music-org:{versionOracle.SemVer2}",
            "clcrutch/music-org:latest"
        }
    };

    DockerBuild(settings, ".");
});

Task("Push-Docker-Container")
    .IsDependentOn("Build-Docker-Container")
    .Does(() =>
{
    DockerPush($"clcrutch/music-org:{versionOracle.SemVer2}");
});

//////////////////////////////////////////////////////////////////////
// TASK TARGETS
//////////////////////////////////////////////////////////////////////

Task("Default")
    .IsDependentOn("Push-Docker-Container");

//////////////////////////////////////////////////////////////////////
// EXECUTION
//////////////////////////////////////////////////////////////////////

RunTarget(target);
