function parseDfResponse(data) {
    var trimData = data.trim();
    var splitData = trimData.split("\n");
    var step = [];
    var i = 0;
    splitData.forEach((value) => {
        a = value.replaceAll("++", "+");

        b = a.replaceAll("++", "+");
        c = b.replaceAll("++", "+");
        d = c.replaceAll("++", "+");
        step[i] = d;
        i++;
    });

    var key = 0;
    var join = [];
    step.forEach((value) => {
        if (key != 0) {
            further = value.split("+");
            join[further[0]] = [];
            join[further[0]]['1k_blocks'] = further[1];
            join[further[0]]['used'] = further[2];
            join[further[0]]['available'] = further[3];
            join[further[0]]['usage_percentage'] = further[4];
            join[further[0]]['mount_point'] = further[5];
            join[further[0]]['mounted_on'] = further[8];
        }
        key++;
    });
    return join;
}

module.exports = { parseDfResponse }