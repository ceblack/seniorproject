def html_table_generator(valueMatrix):
    prefix = "<table cellpadding=\"3\">"
    suffix = "</table>"
    headers = valueMatrix[0]
    headerString = "<tr>"
    for h in headers:
        tempString = "<th>"+h+"</th>"
        headerString = headerString + tempString
    headerString = headerString + "</tr>"
    tableString = ""
    for i in range(1,len(valueMatrix)):
        tempStringList = []
        for val in valueMatrix[i]:
            if(type(val)!=str):
                val = str(round(float(val),3))
            val = right_pad(3, val)
            tempStringList.append("<td>"+val+"</td>")
        rowString = " ".join(tempStringList)
        rowString = "<tr>"+rowString+"</tr>"
        tableString = tableString + rowString
    table = prefix + headerString + tableString + suffix
    return(table)

def plotly_height_changer(plotlyURL, desiredHeight):
    newURL = plotlyURL.replace('height="525"','height="'+str(int(desiredHeight))+'"')
    return(newURL)

def right_pad(padNum, val):
    try:
        val = str(round(float(val),padNum))
        while(len(val[val.index("."):])<4):
            val = val + "0"
        return(val)
    except:
        return(val)
