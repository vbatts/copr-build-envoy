
load("@bazel_tools//tools/build_defs/pkg:rpm.bzl", "pkg_rpm")

pkg_rpm(
	name = "envoy",
	spec_file = ":envoy.spec",
	version = "1.4.0",
	changelog = ":envoy.spec",
	data = [
		":envoy.spec"
	],
)
