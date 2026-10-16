package gpcm

import (
	"wwfc/logging"
	"wwfc/networkpolicy"
)

var loginNetworkPolicy *networkpolicy.Policy

func (g *GameSpySession) checkLoginNetwork() (string, bool) {
	ip, err := networkpolicy.ClientIP(g.RemoteAddr)
	if err != nil {
		g.replyError(ErrLogin)
		return "", false
	}
	if loginNetworkPolicy == nil {
		return ip.String(), true
	}
	blocked, lookupErr := loginNetworkPolicy.Check(ctx, ip)
	if lookupErr != nil {
		logging.Warn(g.ModuleName, "VPN lookup unavailable; fail-closed:", config.VPNFilter.FailClosed)
	}
	if !blocked {
		return ip.String(), true
	}
	message := "This network is blocked. Disable your VPN/proxy or contact an administrator."
	if lookupErr != nil {
		message = "Network verification is temporarily unavailable. Please try again later."
	}
	g.replyError(GPError{
		ErrorCode: ErrLogin.ErrorCode, ErrorString: message, Fatal: true,
		WWFCMessage: WWFCErrorMessage{ErrorCode: 22012, MessageRMC: map[byte]string{LangEnglish: message, LangDutch: message}},
	})
	return "", false
}
