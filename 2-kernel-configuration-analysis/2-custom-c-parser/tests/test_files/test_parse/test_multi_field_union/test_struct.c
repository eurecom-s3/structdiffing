struct fb_info {
	union {
		 char __iomem *screen_base;	
		 char *screen_buffer;
		 const int a,b;
	};
	struct {
		int a;
	};
	union {
		union {
			int b;
		};
		int a;
	};
	union x_name {

	};
	union {

	} y_name;
};