
install-azcopy:
	# install azcopy in the virtual environment
	# see also: https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10

	# download azcopy
	wget https://aka.ms/downloadazcopy-v10-linux
	tar -xvf downloadazcopy-v10-linux

	# install
	rm -f .venv/bin/azcopy
	mv ./azcopy_linux_amd64_*/azcopy .venv/bin/azcopy

	# clean up
	rm downloadazcopy-v10-linux
	rm -rf ./azcopy_linux_amd64_*/ downloadazcopy-v10-linux
