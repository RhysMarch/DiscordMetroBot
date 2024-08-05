# Tyne and Wear Metro Discord Bot

This Discord bot provides Tyne and Wear Metro service updates and train times. 

- **Automatic Updates**: Fetches and summarises Metro service updates hourly from the Nexus website, posting them to a dedicated channel.
- **Train Times**: Use the !times <station> command (or !time) to get the next upcoming train times for any Metro station.
- **Map**: Displays a pinned map of the Metro network for quick reference.
- The bot skips checking for updates between 1 AM and 5 AM to reduce API requests.
- Times are deleted after 5 minutes to keep the info fresh

## Usage

!time <station name/code>: Get train times for a station (e.g., !times Airport or !times APT).

## Nexus Metro API
This bot fetches live train times directly from the Nexus Metro API.

https://metro-rti.nexus.org.uk/api/times/{Code}/{Platform}

**Example:** To get times for trains arriving at Platform 1 of Monument station (code MTS):

https://metro-rti.nexus.org.uk/api/times/MTS/1

## Stations

| Station Name          | Code  | Station Name     | Code  | Station Name      | Code  |
|------------------------|-------|-------------------|-------|--------------------|-------|
| Airport               | APT   | Heworth           | HTH   | Simonside         | SMD   |
| Bank Foot             | BFT   | Howdon            | HOW   | South Gosforth    | SGF   |
| Bede                  | BDE   | Ilford Road       | ILF   | South Hylton      | SHL   |
| Benton                | BTN   | Jarrow            | JAR   | South Shields     | SSS   |
| Brockley Whins        | BYW   | Jesmond           | JES   | St James          | SJM   |
| Byker                 | BYK   | Kingston Park     | KSP   | St Peters         | MSP   |
| Callerton Parkway     | CAL   | Longbenton        | LBN   | Stadium of Light  | SFC   |
| Central               | CEN   | Manors            | MAN   | Sunderland        | SUN   |
| Chichester            | CHI   | Meadow Well       | MWL   | Tyne Dock         | TDK   |
| Chillingham Road      | CRD   | Millfield         | MLF   | Tynemouth         | TYN   |
| Cullercoats           | CUL   | Monkseaton        | MSN   | University        | UNI   |
| East Boldon           | EBO   | Monument (N/S)    | MTS   | Wallsend          | WSD   |
| Fawdon                | FAW   | Monument (W/E)    | MTW   | Walkergate        | WKG   |
| Felling               | FEL   | Northumberland Pk | NPK   | Wansbeck Road     | WBR   |
| Fellgate              | FGT   | North Shields     | NSH   | West Jesmond      | WJS   |
| Four Lane Ends        | FLE   | Pallion           | PAL   | West Monkseaton   | WMN   |
| Gateshead             | GHD   | Palmersville      | PMV   | Whitley Bay       | WTL   |
| Gateshead Stadium     | GST   | Park Lane         | PLI   | Pelaw             | PLW   |
| Hadrian Road          | HDR   | Percy Main        | PCM   | Regent Centre     | RGC   |
| Haymarket             | HAY   | Seaburn           | SBN   | Shiremoor         | SMR   |
