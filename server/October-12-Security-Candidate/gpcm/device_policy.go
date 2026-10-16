package gpcm

const defaultDolphinDeviceID uint32 = 0x0403ac68

func prohibitedDeviceID(id uint32, allowDefault bool) bool {
	if id == defaultDolphinDeviceID {
		return !allowDefault
	}
	for _, leaked := range commonDeviceIds {
		if id == leaked {
			return true
		}
	}
	return false
}
