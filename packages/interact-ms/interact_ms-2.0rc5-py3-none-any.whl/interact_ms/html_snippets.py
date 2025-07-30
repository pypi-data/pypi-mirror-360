""" HTML Snippets to be injected throughout
"""


INTERACT_HEADER = """
    <dev class  = "header">
        <dev class = "header-left">
            
            <img src="http://{server_address}:5000/static/qsb-logo.png"
            class = "inSPIRE-logo-nobg" 
            width = "180px"
            onclick="goHome('{server_address}')"/>
        </dev>
        
        <!-- Header Center-->
        <dev class = "home">
            <a href=http://{server_address}:5000/interact-page/home> <p class = "home-text"> Home </p>
            </a>
        </dev>

        <dev class = "about-us">
            <a href=http://{server_address}:5000/interact-page/about> <p class = "about-us-text"> About </p>
            </a>
        </dev>

        <dev class = "contact">
            <a href=http://{server_address}:5000/interact-page/contact> <p class = "contact-text"> Contact </p>
            </a>
        </dev>

        <dev class = "FAQ">
            <a href=http://{server_address}:5000/interact-page/faq> <p class = "FAQ-text"> FAQ </p>
            </a>
        </dev>

        <dev class = "view-queue">
            <a href=http://{server_address}:5000/interact-page/view-queue> <p class = "view-queue-text">Job Queue</p>
            </a>
        </dev>

        <dev class = "header-right">

            <button type="button" class = "button-git"  
                onclick="location.href='https://github.com/QuantSysBio/interact-ms';">
                <p>&nbsp;&nbsp;GIT HUB</p>
            </button>
        

       
            <button type="button" class = "button"
                onclick="location.href='http://{server_address}:5000/interact';">
                <p>&nbsp;&nbsp;&nbsp;&nbsp;GET STARTED</p>
            </button>
        </dev>

    </dev>
"""

INTERACT_FOOTER = """
    <div class = "bottom">
        <div class = "footer">
            <p>
                <b>
                    Disclaimer: interact-ms, PEPSeek, and inSPIRE are available
                    under an open source license. Check licenses if installing
                    additional supported tools.<br>
                    If you use this tool, please don't forget 
                    to cite related <a href = "http://{server_address}:5000/interact-page/references">articles</a>.
                </b>
            </p>
        </div>
    </div>
"""
