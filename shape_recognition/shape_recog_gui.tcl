#############################################################################
# Generated by PAGE version 4.14
# in conjunction with Tcl version 8.6
set vTcl(timestamp) ""


if {!$vTcl(borrow)} {

set vTcl(actual_gui_bg) #d9d9d9
set vTcl(actual_gui_fg) #000000
set vTcl(actual_gui_menu_bg) #d9d9d9
set vTcl(actual_gui_menu_fg) #000000
set vTcl(complement_color) #d9d9d9
set vTcl(analog_color_p) #d9d9d9
set vTcl(analog_color_m) #d9d9d9
set vTcl(active_fg) #000000
set vTcl(actual_gui_menu_active_bg)  #d8d8d8
set vTcl(active_menu_fg) #000000
}

#################################
#LIBRARY PROCEDURES
#


if {[info exists vTcl(sourcing)]} {

proc vTcl:project:info {} {
    set base .top37
    global vTcl
    set base $vTcl(btop)
    if {$base == ""} {
        set base .top37
    }
    namespace eval ::widgets::$base {
        set dflt,origin 0
        set runvisible 1
    }
    set site_3_0 $base.lab45
    set site_3_0 $base.lab49
    set site_3_0 $base.lab54
    set site_3_0 $base.lab58
    set site_3_0 $base.can63
    set site_3_0 $base.lab66
    namespace eval ::widgets_bindings {
        set tagslist _TopLevel
    }
    namespace eval ::vTcl::modules::main {
        set procs {
        }
        set compounds {
        }
        set projectType single
    }
}
}

#################################
# GENERATED GUI PROCEDURES
#

proc vTclWindow.top37 {base} {
    if {$base == ""} {
        set base .top37
    }
    if {[winfo exists $base]} {
        wm deiconify $base; return
    }
    set top $base
    ###################
    # CREATING WIDGETS
    ###################
    vTcl::widgets::core::toplevel::createCmd $top -class Toplevel \
        -background {#d9d9d9} -highlightcolor black 
    wm focusmodel $top passive
    wm geometry $top 794x691+459+134
    update
    # set in toplevel.wgt.
    global vTcl
    global img_list
    set vTcl(save,dflt,origin) 0
    wm maxsize $top 1905 1050
    wm minsize $top 1 1
    wm overrideredirect $top 0
    wm resizable $top 1 1
    wm deiconify $top
    wm title $top "Shape Recognition"
    vTcl:DefineAlias "$top" "Toplevel1" vTcl:Toplevel:WidgetProc "" 1
    canvas $top.can38 \
        -background {#d9d9d9} -borderwidth 2 -closeenough 1.0 -height 161 \
        -highlightcolor black -insertbackground black -relief ridge \
        -selectbackground {#c4c4c4} -selectforeground black -width 171 
    vTcl:DefineAlias "$top.can38" "view_0" vTcl:WidgetProc "Toplevel1" 1
    canvas $top.can40 \
        -background {#d9d9d9} -borderwidth 2 -closeenough 1.0 -height 75 \
        -highlightcolor black -insertbackground black -relief ridge \
        -selectbackground {#c4c4c4} -selectforeground black -width 125 
    vTcl:DefineAlias "$top.can40" "view_1" vTcl:WidgetProc "Toplevel1" 1
    canvas $top.can41 \
        -background {#d9d9d9} -borderwidth 2 -closeenough 1.0 -height 75 \
        -highlightcolor black -insertbackground black -relief ridge \
        -selectbackground {#c4c4c4} -selectforeground black -width 125 
    vTcl:DefineAlias "$top.can41" "view_2" vTcl:WidgetProc "Toplevel1" 1
    canvas $top.can42 \
        -background {#d9d9d9} -borderwidth 2 -closeenough 1.0 -height 161 \
        -highlightcolor black -insertbackground black -relief ridge \
        -selectbackground {#c4c4c4} -selectforeground black -width 171 
    vTcl:DefineAlias "$top.can42" "view_3" vTcl:WidgetProc "Toplevel1" 1
    canvas $top.can43 \
        -background {#d9d9d9} -borderwidth 2 -closeenough 1.0 -height 161 \
        -highlightcolor black -insertbackground black -relief ridge \
        -selectbackground {#c4c4c4} -selectforeground black -width 171 
    vTcl:DefineAlias "$top.can43" "view_4" vTcl:WidgetProc "Toplevel1" 1
    canvas $top.can44 \
        -background {#d9d9d9} -borderwidth 2 -closeenough 1.0 -height 161 \
        -highlightcolor black -insertbackground black -relief ridge \
        -selectbackground {#c4c4c4} -selectforeground black -width 171 
    vTcl:DefineAlias "$top.can44" "view_5" vTcl:WidgetProc "Toplevel1" 1
    labelframe $top.lab45 \
        -foreground black -text General -background {#d9d9d9} -height 115 \
        -highlightcolor black -width 200 
    vTcl:DefineAlias "$top.lab45" "Labelframe1" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.lab45
    button $site_3_0.but46 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text Initialize 
    vTcl:DefineAlias "$site_3_0.but46" "initialize" vTcl:WidgetProc "Toplevel1" 1
    button $site_3_0.but47 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text Configure 
    vTcl:DefineAlias "$site_3_0.but47" "configure" vTcl:WidgetProc "Toplevel1" 1
    button $site_3_0.but48 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text Start 
    vTcl:DefineAlias "$site_3_0.but48" "start_main" vTcl:WidgetProc "Toplevel1" 1
    button $site_3_0.but68 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text Stop 
    vTcl:DefineAlias "$site_3_0.but68" "stop_main" vTcl:WidgetProc "Toplevel1" 1
    place $site_3_0.but46 \
        -in $site_3_0 -x 10 -y 20 -width 181 -relwidth 0 -height 26 \
        -relheight 0 -anchor nw -bordermode ignore 
    place $site_3_0.but47 \
        -in $site_3_0 -x 10 -y 50 -width 181 -height 26 -anchor nw \
        -bordermode ignore 
    place $site_3_0.but48 \
        -in $site_3_0 -x 10 -y 80 -width 91 -relwidth 0 -height 26 \
        -relheight 0 -anchor nw -bordermode ignore 
    place $site_3_0.but68 \
        -in $site_3_0 -x 100 -y 80 -width 91 -height 26 -anchor nw \
        -bordermode ignore 
    labelframe $top.lab49 \
        -foreground black -text UR10 -background {#d9d9d9} -height 145 \
        -highlightcolor black -width 200 
    vTcl:DefineAlias "$top.lab49" "Labelframe2" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.lab49
    button $site_3_0.but50 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text {Move to "Home"} 
    vTcl:DefineAlias "$site_3_0.but50" "to_home" vTcl:WidgetProc "Toplevel1" 1
    button $site_3_0.but51 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text {Move to base} 
    vTcl:DefineAlias "$site_3_0.but51" "to_base" vTcl:WidgetProc "Toplevel1" 1
    button $site_3_0.but52 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text Up 
    vTcl:DefineAlias "$site_3_0.but52" "move_up" vTcl:WidgetProc "Toplevel1" 1
    button $site_3_0.but53 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text Down 
    vTcl:DefineAlias "$site_3_0.but53" "move_down" vTcl:WidgetProc "Toplevel1" 1
    button $site_3_0.but38 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text CW 
    vTcl:DefineAlias "$site_3_0.but38" "rotateHandCW" vTcl:WidgetProc "Toplevel1" 1
    button $site_3_0.but39 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text CCW 
    vTcl:DefineAlias "$site_3_0.but39" "rotateHandCCW" vTcl:WidgetProc "Toplevel1" 1
    place $site_3_0.but50 \
        -in $site_3_0 -x 10 -y 20 -width 181 -relwidth 0 -height 26 \
        -relheight 0 -anchor nw -bordermode ignore 
    place $site_3_0.but51 \
        -in $site_3_0 -x 10 -y 50 -width 181 -height 26 -anchor nw \
        -bordermode ignore 
    place $site_3_0.but52 \
        -in $site_3_0 -x 10 -y 80 -width 91 -relwidth 0 -height 26 \
        -relheight 0 -anchor nw -bordermode ignore 
    place $site_3_0.but53 \
        -in $site_3_0 -x 100 -y 80 -width 91 -height 26 -anchor nw \
        -bordermode ignore 
    place $site_3_0.but38 \
        -in $site_3_0 -x 10 -y 110 -width 91 -relwidth 0 -height 26 \
        -relheight 0 -anchor nw -bordermode ignore 
    place $site_3_0.but39 \
        -in $site_3_0 -x 100 -y 110 -width 91 -height 26 -anchor nw \
        -bordermode ignore 
    labelframe $top.lab54 \
        -foreground black -text iLimb -background {#d9d9d9} -height 115 \
        -highlightcolor black -width 200 
    vTcl:DefineAlias "$top.lab54" "Labelframe3" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.lab54
    button $site_3_0.but55 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text {Rest pose} 
    vTcl:DefineAlias "$site_3_0.but55" "to_rest" vTcl:WidgetProc "Toplevel1" 1
    button $site_3_0.but56 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text {Feedback pinch touch} 
    vTcl:DefineAlias "$site_3_0.but56" "closeHand" vTcl:WidgetProc "Toplevel1" 1
    button $site_3_0.but57 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text {Open hand} 
    vTcl:DefineAlias "$site_3_0.but57" "openHand" vTcl:WidgetProc "Toplevel1" 1
    place $site_3_0.but55 \
        -in $site_3_0 -x 10 -y 20 -width 181 -relwidth 0 -height 26 \
        -relheight 0 -anchor nw -bordermode ignore 
    place $site_3_0.but56 \
        -in $site_3_0 -x 10 -y 50 -width 181 -height 26 -anchor nw \
        -bordermode ignore 
    place $site_3_0.but57 \
        -in $site_3_0 -x 10 -y 80 -width 181 -height 26 -anchor nw \
        -bordermode ignore 
    labelframe $top.lab58 \
        -foreground black -text {Tactile Sensors} -background {#d9d9d9} \
        -height 85 -highlightcolor black -width 200 
    vTcl:DefineAlias "$top.lab58" "Labelframe4" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.lab58
    button $site_3_0.but59 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text Calibrate 
    vTcl:DefineAlias "$site_3_0.but59" "calibrate" vTcl:WidgetProc "Toplevel1" 1
    button $site_3_0.but61 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text Start 
    vTcl:DefineAlias "$site_3_0.but61" "start_sensor" vTcl:WidgetProc "Toplevel1" 1
    button $site_3_0.but62 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text Stop 
    vTcl:DefineAlias "$site_3_0.but62" "stop_sensor" vTcl:WidgetProc "Toplevel1" 1
    place $site_3_0.but59 \
        -in $site_3_0 -x 10 -y 50 -width 181 -relwidth 0 -height 26 \
        -relheight 0 -anchor nw -bordermode ignore 
    place $site_3_0.but61 \
        -in $site_3_0 -x 10 -y 20 -width 91 -relwidth 0 -height 26 \
        -relheight 0 -anchor nw -bordermode ignore 
    place $site_3_0.but62 \
        -in $site_3_0 -x 100 -y 20 -width 91 -relwidth 0 -height 26 \
        -relheight 0 -anchor nw -bordermode ignore 
    canvas $top.can63 \
        -background {#d9d9d9} -borderwidth 2 -closeenough 1.0 -height 141 \
        -highlightcolor black -insertbackground black -relief ridge \
        -selectbackground {#c4c4c4} -selectforeground black -width 561 
    vTcl:DefineAlias "$top.can63" "tactile_thumb" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.can63
    canvas $site_3_0.can64 \
        -background {#d9d9d9} -borderwidth 2 -closeenough 1.0 -height 141 \
        -highlightcolor black -insertbackground black -relief ridge \
        -selectbackground {#c4c4c4} -selectforeground black -width 561 
    vTcl:DefineAlias "$site_3_0.can64" "Canvas4_14" vTcl:WidgetProc "Toplevel1" 1
    place $site_3_0.can64 \
        -in $site_3_0 -x 330 -y 571 -width 561 -height 141 -anchor nw \
        -bordermode ignore 
    canvas $top.can65 \
        -background {#d9d9d9} -borderwidth 2 -closeenough 1.0 -height 141 \
        -highlightcolor black -insertbackground black -relief ridge \
        -selectbackground {#c4c4c4} -selectforeground black -width 561 
    vTcl:DefineAlias "$top.can65" "tactile_index" vTcl:WidgetProc "Toplevel1" 1
    labelframe $top.lab66 \
        -foreground black -text Status -background {#d9d9d9} -height 95 \
        -highlightcolor black -width 200 
    vTcl:DefineAlias "$top.lab66" "status" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.lab66
    label $site_3_0.lab67 \
        -activebackground {#f9f9f9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -justify left -text {Nothing to do.} 
    vTcl:DefineAlias "$site_3_0.lab67" "statusText" vTcl:WidgetProc "Toplevel1" 1
    place $site_3_0.lab67 \
        -in $site_3_0 -x 3 -y 20 -width 195 -relwidth 0 -height 68 \
        -relheight 0 -anchor nw -bordermode ignore 
    button $top.but69 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -state active -text {Visualize point cloud} 
    vTcl:DefineAlias "$top.but69" "visualize" vTcl:WidgetProc "Toplevel1" 1
    button $top.but70 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text {Compute convex hull} 
    vTcl:DefineAlias "$top.but70" "visualize_surface" vTcl:WidgetProc "Toplevel1" 1
    button $top.but71 \
        -activebackground {#d9d9d9} -activeforeground black \
        -background {#d9d9d9} -foreground {#000000} -highlightcolor black \
        -text {Detect shape} 
    vTcl:DefineAlias "$top.but71" "detect_shape" vTcl:WidgetProc "Toplevel1" 1
    ###################
    # SETTING GEOMETRY
    ###################
    place $top.can38 \
        -in $top -x 10 -y 10 -width 180 -relwidth 0 -height 180 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.can40 \
        -in $top -x 200 -y 10 -width 180 -height 180 -anchor nw \
        -bordermode ignore 
    place $top.can41 \
        -in $top -x 390 -y 10 -width 180 -height 180 -anchor nw \
        -bordermode ignore 
    place $top.can42 \
        -in $top -x 10 -y 200 -width 180 -height 180 -anchor nw \
        -bordermode ignore 
    place $top.can43 \
        -in $top -x 200 -y 200 -width 180 -height 180 -anchor nw \
        -bordermode ignore 
    place $top.can44 \
        -in $top -x 390 -y 200 -width 180 -height 180 -anchor nw \
        -bordermode ignore 
    place $top.lab45 \
        -in $top -x 580 -y 10 -width 200 -relwidth 0 -height 115 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.lab49 \
        -in $top -x 580 -y 130 -width 200 -relwidth 0 -height 145 \
        -relheight 0 -anchor nw -bordermode ignore 
    place $top.lab54 \
        -in $top -x 580 -y 280 -width 200 -relwidth 0 -height 115 \
        -relheight 0 -anchor nw -bordermode ignore 
    place $top.lab58 \
        -in $top -x 580 -y 400 -width 200 -relwidth 0 -height 85 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.can63 \
        -in $top -x 10 -y 390 -width 561 -relwidth 0 -height 141 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.can65 \
        -in $top -x 10 -y 540 -width 561 -height 141 -anchor nw \
        -bordermode ignore 
    place $top.lab66 \
        -in $top -x 580 -y 583 -width 200 -relwidth 0 -height 95 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.but69 \
        -in $top -x 580 -y 490 -width 201 -relwidth 0 -height 26 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.but70 \
        -in $top -x 580 -y 520 -width 201 -height 26 -anchor nw \
        -bordermode ignore 
    place $top.but71 \
        -in $top -x 580 -y 550 -width 201 -height 26 -anchor nw \
        -bordermode ignore 

    vTcl:FireEvent $base <<Ready>>
}

#############################################################################
## Binding tag:  _TopLevel

bind "_TopLevel" <<Create>> {
    if {![info exists _topcount]} {set _topcount 0}; incr _topcount
}
bind "_TopLevel" <<DeleteWindow>> {
    if {[set ::%W::_modal]} {
                vTcl:Toplevel:WidgetProc %W endmodal
            } else {
                destroy %W; if {$_topcount == 0} {exit}
            }
}
bind "_TopLevel" <Destroy> {
    if {[winfo toplevel %W] == "%W"} {incr _topcount -1}
}

set btop ""
if {$vTcl(borrow)} {
    set btop .bor[expr int([expr rand() * 100])]
    while {[lsearch $btop $vTcl(tops)] != -1} {
        set btop .bor[expr int([expr rand() * 100])]
    }
}
set vTcl(btop) $btop
Window show .
Window show .top37 $btop
if {$vTcl(borrow)} {
    $btop configure -background plum
}

