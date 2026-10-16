package database

func hasKnownIdentifier[T comparable](values []T, empty T) bool {
	for _, value := range values {
		if value != empty {
			return true
		}
	}
	return false
}

// Only an explicitly permissive policy may add another identifier to an
// existing account. Empty or misspelled policies are restrictive.
func allowAdditionalIdentifier(policy string, previousIP *string, currentIP string) bool {
	switch policy {
	case "always":
		return true
	case "SameIPAddress":
		return previousIP != nil && *previousIP != "" && currentIP == *previousIP
	default:
		return false
	}
}
