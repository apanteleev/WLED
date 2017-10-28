/*
 * Receives client input
 */

void handleSettingsSet()
{
  if (server.hasArg("CSSID")) clientssid = server.arg("CSSID");
  if (server.hasArg("CPASS"))
  {
    if (!server.arg("CPASS").indexOf('*') == 0)
    {
      DEBUG_PRINTLN("Setting pass");
      clientpass = server.arg("CPASS");
    }
  }
  if (server.hasArg("CMDNS")) cmdns = server.arg("CMDNS");
  if (server.hasArg("APSSID")) apssid = server.arg("APSSID");
  if (server.hasArg("APHSSID"))
  {
    aphide = 1;
  } else
  {
    aphide = 0;
  }
  if (server.hasArg("APPASS"))
  {
    if (!server.arg("APPASS").indexOf('*') == 0) appass = server.arg("APPASS");
  }
  if (server.hasArg("APCHAN"))
  {
    int chan = server.arg("APCHAN").toInt();
    if (chan > 0 && chan < 14) apchannel = chan;
  }
  if (server.hasArg("RESET")) //might be dangerous in case arg is always sent
  {
    clearEEPROM();
    server.send(200, "text/plain", "Settings erased. Please wait for light to turn back on, then go to main page...");
    reset();
  }
  if (server.hasArg("CSIP0"))
  {
    int i = server.arg("CSIP0").toInt();
    if (i >= 0 && i <= 255) staticip[0] = i;
  }
  if (server.hasArg("CSIP1"))
  {
    int i = server.arg("CSIP1").toInt();
    if (i >= 0 && i <= 255) staticip[1] = i;
  }
  if (server.hasArg("CSIP2"))
  {
    int i = server.arg("CSIP2").toInt();
    if (i >= 0 && i <= 255) staticip[2] = i;
  }
  if (server.hasArg("CSIP3"))
  {
    int i = server.arg("CSIP3").toInt();
    if (i >= 0 && i <= 255) staticip[3] = i;
  }
  if (server.hasArg("CSGW0"))
  {
    int i = server.arg("CSGW0").toInt();
    if (i >= 0 && i <= 255) staticgateway[0] = i;
  }
  if (server.hasArg("CSGW1"))
  {
    int i = server.arg("CSGW1").toInt();
    if (i >= 0 && i <= 255) staticgateway[1] = i;
  }
  if (server.hasArg("CSGW2"))
  {
    int i = server.arg("CSGW2").toInt();
    if (i >= 0 && i <= 255) staticgateway[2] = i;
  }
  if (server.hasArg("CSGW3"))
  {
    int i = server.arg("CSGW3").toInt();
    if (i >= 0 && i <= 255) staticgateway[3] = i;
  }
  if (server.hasArg("CSSN0"))
  {
    int i = server.arg("CSSN0").toInt();
    if (i >= 0 && i <= 255) staticsubnet[0] = i;
  }
  if (server.hasArg("CSSN1"))
  {
    int i = server.arg("CSSN1").toInt();
    if (i >= 0 && i <= 255) staticsubnet[1] = i;
  }
  if (server.hasArg("CSSN2"))
  {
    int i = server.arg("CSSN2").toInt();
    if (i >= 0 && i <= 255) staticsubnet[2] = i;
  }
  if (server.hasArg("CSSN3"))
  {
    int i = server.arg("CSSN3").toInt();
    if (i >= 0 && i <= 255) staticsubnet[3] = i;
  }
  if (server.hasArg("DESC")) serverDescription = server.arg("DESC");
  useHSBDefault = server.hasArg("COLMD");
  useHSB = useHSBDefault;
  if (server.hasArg("LEDCN"))
  {
    int i = server.arg("LEDCN").toInt();
    if (i >= 0 && i <= 255) ledcount = i;
    strip.setLedCount(ledcount);
  }
  if (server.hasArg("CBEOR"))
  {
    col_s[0] = col[0];
    col_s[1] = col[1];
    col_s[2] = col[2];
    bri_s = bri;
    effectDefault = effectCurrent;
    effectSpeedDefault = effectSpeed;
  } else {
    if (server.hasArg("CLDFR"))
    {
      int i = server.arg("CLDFR").toInt();
      if (i >= 0 && i <= 255) col_s[0] = i;
    }
    if (server.hasArg("CLDFG"))
    {
      int i = server.arg("CLDFG").toInt();
      if (i >= 0 && i <= 255) col_s[1] = i;
    }
    if (server.hasArg("CLDFB"))
    {
      int i = server.arg("CLDFB").toInt();
      if (i >= 0 && i <= 255) col_s[2] = i;
    }
    if (server.hasArg("CLDFW"))
    {
      int i = server.arg("CLDFW").toInt();
      if (i >= 0 && i <= 255)
      {
        useRGBW = true;
        white_s = i;
      } else {
        useRGBW = false;
        white_s = 0;
      }
    }
    if (server.hasArg("CLDFA"))
    {
      int i = server.arg("CLDFA").toInt();
      if (i >= 0 && i <= 255) bri_s = i;
    }
    turnOnAtBoot = server.hasArg("BOOTN");
    if (server.hasArg("FXDEF"))
    {
      int i = server.arg("FXDEF").toInt();
      if (i >= 0 && i <= 255) effectDefault = i;
    }
    if (server.hasArg("SXDEF"))
    {
      int i = server.arg("SXDEF").toInt();
      if (i >= 0 && i <= 255) effectSpeedDefault = i;
    }
  }
  useGammaCorrectionBri = server.hasArg("GCBRI");
  useGammaCorrectionRGB = server.hasArg("GCRGB");
  buttonEnabled = server.hasArg("BTNON");
  fadeTransition = server.hasArg("TFADE");
  sweepTransition = server.hasArg("TSWEE");
  sweepDirection = !server.hasArg("TSDIR");
  if (server.hasArg("TDLAY"))
  {
    int i = server.arg("TDLAY").toInt();
    if (i > 0){
      transitionDelay = i;
    }
  }
  if (server.hasArg("TLBRI"))
  {
    bri_nl = server.arg("TLBRI").toInt();
  }
  if (server.hasArg("TLDUR"))
  {
    int i = server.arg("TLDUR").toInt();
    if (i > 0) nightlightDelayMins = i;
  }
  nightlightFade = server.hasArg("TLFDE");
  if (server.hasArg("NUDPP"))
  {
    udpPort = server.arg("NUDPP").toInt();
  }
  receiveNotifications = server.hasArg("NRCVE");
  receiveNotificationsDefault = receiveNotifications;
  if (server.hasArg("NRBRI"))
  {
    int i = server.arg("NRBRI").toInt();
    if (i > 0) bri_n = i;
  }
  notifyDirectDefault = server.hasArg("NSDIR");
  notifyDirect = notifyDirectDefault;
  notifyButton = server.hasArg("NSBTN");
  alexaEnabled = server.hasArg("ALEXA");
  if (server.hasArg("AINVN")) alexaInvocationName = server.arg("AINVN");
  alexaNotify = server.hasArg("NSALX");
  ntpEnabled = server.hasArg("NTPON");
  if (server.hasArg("OLDEF"))
  {
    int i = server.arg("OLDEF").toInt();
    if (i >= 0  && i <= 255) overlayDefault = i;
  }
  if (server.hasArg("WOFFS"))
  {
    int i = server.arg("WOFFS").toInt();
    if (i >= 0  && i <= 255) arlsOffset = i;
    arlsSign = true;
    if (server.hasArg("WOFFN"))
    {
      arlsSign = false;
      arlsOffset = -arlsOffset;
    }
  }
  if (server.hasArg("OPASS"))
  {
    if (!ota_lock)
    {
      if (server.arg("OPASS").length() > 0)
      otapass = server.arg("OPASS");
    } else if (!server.hasArg("NOOTA"))
    {
      if (otapass.equals(server.arg("OPASS")))
      {
        ota_lock = false;
      }
    }
  }
  if (server.hasArg("NOOTA")) ota_lock = true;
  saveSettingsToEEPROM();
}

boolean handleSet(String req)
{
   boolean effectUpdated = false;
   if (!(req.indexOf("win") >= 0)) {
        if (req.indexOf("get-settings") >= 0)
        {
          XML_response_settings();
          return true;
        }
        return false;
   }
   int pos = 0;
   pos = req.indexOf("A=");
   if (pos > 0) {
      bri = req.substring(pos + 2).toInt();
   }
   pos = req.indexOf("R=");
   if (pos > 0) {
      col[0] = req.substring(pos + 2).toInt();
   }
   pos = req.indexOf("G=");
   if (pos > 0) {
      col[1] = req.substring(pos + 2).toInt();
   }
   pos = req.indexOf("B=");
   if (pos > 0) {
      col[2] = req.substring(pos + 2).toInt();
   }
   pos = req.indexOf("W=");
   if (pos > 0) {
      white = req.substring(pos + 2).toInt();
   }
   pos = req.indexOf("FX=");
   if (pos > 0) {
      if (effectCurrent != req.substring(pos + 3).toInt())
      {
        effectCurrent = req.substring(pos + 3).toInt();
        strip.setMode(effectCurrent);
        effectUpdated = true;
      }
   }
   pos = req.indexOf("SX=");
   if (pos > 0) {
      if (effectSpeed != req.substring(pos + 3).toInt())
      {
        effectSpeed = req.substring(pos + 3).toInt();
        strip.setSpeed(effectSpeed);
        effectUpdated = true;
      }
   }
   pos = req.indexOf("MD=");
   if (pos > 0) {
      useHSB = req.substring(pos + 3).toInt();
   }
   pos = req.indexOf("OL=");
   if (pos > 0) {
        overlayCurrent = req.substring(pos + 3).toInt();
        strip.unlockAll();
   }
   pos = req.indexOf("I=");
   if (pos > 0){
      int index = req.substring(pos + 2).toInt();
      pos = req.indexOf("I2=");
      if (pos > 0){
        int index2 = req.substring(pos + 3).toInt();
        strip.setRange(index, index2);
      } else
      {
        strip.setIndividual(index);
      }
   }
   if (req.indexOf("SN=") > 0)
   {
      notifyDirect = true;
      if (req.indexOf("SN=0") > 0)
      {
        notifyDirect = false;
      }
   }
   if (req.indexOf("RN=") > 0)
   {
      receiveNotifications = true;
      if (req.indexOf("RN=0") > 0)
      {
        receiveNotifications = false;
      }
   }
   if (req.indexOf("NL=") > 0)
   {
      if (req.indexOf("NL=0") > 0)
      {
        nightlightActive = false;
        bri = bri_t;
      } else {
        nightlightActive = true;
        nightlightStartTime = millis();
      }
   }
   pos = req.indexOf("AX=");
   if (pos > 0) {
      auxTime = req.substring(pos + 3).toInt();
      auxActive = true;
      if (auxTime == 0) auxActive = false;
   }
   pos = req.indexOf("T=");
   if (pos > 0) {
      switch (req.substring(pos + 2).toInt())
      {
        case 0: if (bri != 0){bri_last = bri; bri = 0;} break; //off
        case 1: bri = bri_last; break; //on
        default: if (bri == 0) //toggle
        {
          bri = bri_last;
        } else
        {
          bri_last = bri;
          bri = 0;
        }
      }
   }
   pos = req.indexOf("IN");
   if (pos < 1)
   {
      XML_response();
   }
   pos = req.indexOf("NN");
   if (pos > 0)
   {
      colorUpdated(5);
      return true;
   }
   if (effectUpdated)
   {
      colorUpdated(6);
   } else
   {
      colorUpdated(1);
   }
   return true;
}
