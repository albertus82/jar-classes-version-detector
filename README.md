JAR Classes Version Detector
============================

[![Build status](https://github.com/albertus82/jar-classes-version-detector/workflows/build/badge.svg)](https://github.com/albertus82/jar-classes-version-detector/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=it.albertus%3Ajar-classes-version-detector&metric=alert_status)](https://sonarcloud.io/dashboard?id=it.albertus%3Ajar-classes-version-detector)

## Requirements
**[Python](https://www.python.org/) 3.6+**

## Usage
`python jarver.py /path/to/library.jar [http://example.com/another.jar .. /path/to/last.jar]`

## Example
`python jarver.py https://repo1.maven.org/maven2/junit/junit/4.12/junit-4.12.jar`

### Output
```
Downloading: 'https://repo1.maven.org/maven2/junit/junit/4.12/junit-4.12.jar'...
Download completed, created temporary file: '/tmp/tmpviuy341u'.
Analyzing archive: 'junit-4.12.jar'...

------------------------ META-INF/MANIFEST.MF ------------------------
Manifest-Version: 1.0
Implementation-Vendor: JUnit
Implementation-Title: JUnit
Implementation-Version: 4.12
Implementation-Vendor-Id: junit
Built-By: jenkins
Build-Jdk: 1.6.0_45
Created-By: Apache Maven 3.0.4
Archiver-Version: Plexus Archiver
----------------------------------------------------------------------

>>> Version 49.0 (Java 5) => 286 classes found: junit/extensions/ActiveTestSuite$1.class, junit/extensions/ActiveTestSuite.class, junit/extensions/RepeatedTest.class, junit/extensions/TestDecorator.class, junit/extensions/TestSetup$1.class, junit/extensions/TestSetup.class, junit/framework/Assert.class, junit/framework/AssertionFailedError.class, junit/framework/ComparisonCompactor.class, junit/framework/ComparisonFailure.class, junit/framework/JUnit4TestAdapter.class, junit/framework/JUnit4TestAdapterCache$1.class, junit/framework/JUnit4TestAdapterCache.class, junit/framework/JUnit4TestCaseFacade.class, junit/framework/Protectable.class, junit/framework/Test.class, junit/framework/TestCase.class, junit/framework/TestFailure.class, junit/framework/TestListener.class, junit/framework/TestResult$1.class, junit/framework/TestResult.class, junit/framework/TestSuite$1.class, junit/framework/TestSuite.class, junit/runner/BaseTestRunner.class, junit/runner/TestRunListener.class, junit/... <<<

Analysis of archive 'junit-4.12.jar' completed.
```
