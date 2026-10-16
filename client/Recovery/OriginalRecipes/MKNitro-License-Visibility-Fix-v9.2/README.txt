Mario Kart Nitro - License Settings visibility fix v9.2 (PAL)

INSTALL
Back up your current MarioKartNitro_Test/Binaries/Code.pul, then replace it with the included file. Keep the MenuOther.szs and Title.szs from v9.1 installed. Fully stop Dolphin and launch normally without a save state.

CHANGES
On each License Settings activation, hide the entire Check Records control, including its label. The previous input disabling and Change Mii focus remain. Set the loaded Mii portrait and its custom ring to the title-screen reference transform: portrait 90x90 at scale 0.5, ring 128x132 inherited from that portrait. This is applied to the loaded panes and does not rely on replacement MenuOther layouts taking effect. All previous v9.1 code changes, including BackModel and item whitening, remain.

VALIDATION
Eight native activation harness cases passed, covering first activation, return activation, missing panes and missing root. Verified hidden flag, exact pane transforms, native return and preserved r31. Pane lookup, selection and text rendering were intercepted in the harness. No Dolphin gameplay/render validation was available. Please check License Settings after a fresh boot and again after returning from Change Miis.

The missing panel/text-backing changes in the supplied screenshot suggest an archive loading mismatch; the cause has not been confirmed. This update directly addresses the Records label and Mii size only.
