package gpcm

import "strings"

func nitroRequiresNameChange(game, name string) bool {
	name = strings.TrimSpace(strings.TrimRight(name, "\x00"))
	return game == "mariokartwii" && (name == "" || strings.EqualFold(name, "Player"))
}

var nitroNameChangeError = GPError{
	ErrorCode:   0x0102,
	ErrorString: "Please choose a non-empty Mii name other than Player and reconnect.",
	Fatal:       true,
	WWFCMessage: WWFCErrorMessage{
		ErrorCode: 22011,
		MessageRMC: map[byte]string{
			LangEnglish: "Please change your Mii name.\nBlank names and Player are not allowed.\nRename your Mii and reconnect.\nError Code: %[1]d",
			LangDutch:   "Verander je Mii-naam.\nEen lege naam of Player is niet toegestaan.\nHernoem je Mii en verbind opnieuw.\nFoutcode: %[1]d",
		},
	},
}
