### ansys-api-additive gRPC Interface Package

This package contains the gRPC interface files for the Additive
service. It is published both as a python and nuget package.

#### Python Installation

Provided that these wheels have been published to public PyPI, they can be installed with:

```
pip install ansys-api-additive
```

#### Python Build

To build the gRPC packages, run:

```
pip install build
python -m build
```

This will create both the source distribution containing just the protofiles along with the wheel containing the protofiles and build Python interface files.

#### Python Manual Deployment

After building the packages, manually deploy them with:

```
pip install twine
twine upload dist/*
```

Note that this is automatically done through CI/CD.

#### Nuget Installation

The nuget package is called `Ansys.Api.Additive` and is published
to a repository on GitHub. To access the repository, you will
need to create a nuget source with your GitHub user credentials.

```
dotnet nuget add source --username USERNAME --password GITHUB_TOKEN --store-password-in-clear-text --name ansys "https://nuget.pkg.github.com/ansys/index.json"
```

For more information, see [GitHub Working with the NuGet registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-nuget-registry).

#### Nuget Build

To build the nuget package, run:

```
dotnet pack csharp/Ansys.Api.Additive.csproj -o package
```

#### Nuget Manual Deployment

Once the nuget package is built, manually deploy it with the following command. Note that this uses the same nuget source created in the Installation step.

```
dotnet nuget push ./**/*.nupkg --source ansys
```

Note that this is automatically done through CI/CD.

#### Automatic Deployment

This repository contains GitHub CI/CD that enables the automatic building of source, wheel, and nuget packages for these gRPC interface files. By default, these are built on PRs, the main branch, and on tags when pushing. Artifacts are uploaded for each PR.

To publicly release the packages, ensure your branch is up-to-date and then push tags. For example, for the version ``v0.5.0``.

```bash
git tag v0.5.0
git push --tags
```

#### Google protobuf files 

The Google third-party protobuf files were obtained from [googleapis](https://github.com/googleapis/googleapis).